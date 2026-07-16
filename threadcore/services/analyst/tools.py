from __future__ import annotations
import base64
from contextvars import ContextVar, Token
import json
import os
from io import BytesIO
from typing import Literal, Optional
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe in async workers
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from langchain_core.tools import tool


DatasetContext = tuple[str, dict]

_dataset_context: ContextVar[DatasetContext | None] = ContextVar(
    "analyst_dataset_context",
    default=None,
)


def set_active_dataset(path: str, schema: dict) -> Token[DatasetContext | None]:
    return _dataset_context.set((path, schema))


def reset_active_dataset(token: Token[DatasetContext | None]) -> None:
    _dataset_context.reset(token)


def _get_active_context() -> DatasetContext:
    context = _dataset_context.get()
    if context is None:
        raise ValueError("No active dataset. Upload a CSV/Excel file first.")
    return context


def _get_active_schema() -> dict | None:
    context = _dataset_context.get()
    return context[1] if context else None


def _load_df() -> pd.DataFrame:
    dataset_path, _ = _get_active_context()
    if not os.path.exists(dataset_path):
        raise ValueError("No active dataset. Upload a CSV/Excel file first.")
    return (
        pd.read_csv(dataset_path, encoding="latin1")
        if dataset_path.endswith(".csv")
        else pd.read_excel(dataset_path)
    )


def _validate_columns(*cols: str | None) -> list[str]:
    
    schema = _get_active_schema()
    if schema is None:
        return []
    known = set(schema.get("columns", []))
    return [c for c in cols if c and c not in known]

# Tool 1 — dataset_summary_tool
@tool
def dataset_summary_tool() -> str:
    """Return dataset shape, dtypes, null counts, and descriptive statistics."""
   
    df = _load_df()

    summary = {
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "describe_numeric": df.describe().round(4).to_dict(),
        "describe_categorical": {},
    }

    for col in df.select_dtypes(include=["object", "category"]).columns[:10]:
        summary["describe_categorical"][col] = (
            df[col].value_counts().head(5).to_dict()
        )

    return json.dumps(summary, indent=2, default=str)


# Tool 2 — pandas_query_tool
@tool
def pandas_query_tool(query: str) -> str:
    """Filter the active dataset with a pandas df.query expression."""
    
    bad_cols = []
    schema = _get_active_schema()
    if schema:
        known = set(schema.get("columns", []))
        tokens = query.replace("(", " ").replace(")", " ").split()
        candidates = [t.strip('"\'') for t in tokens if t.strip('"\'').isidentifier()]
        bad_cols = [c for c in candidates if c not in known and not c[0].isdigit()]

    if bad_cols:
        return (
            f"ERROR — unknown column(s): {bad_cols}.\n"
            f"Available columns: {schema.get('columns', []) if schema else 'unknown'}"
        )

    try:
        df = _load_df()
        result = df.query(query)
        if result.empty:
            return "Query returned 0 rows."
        return result.head(100).to_string(index=False)
    except Exception as exc:
        return f"Query execution error: {exc}"

# Tool 3 — visualization_tool
@tool
def visualization_tool(
    chart_type: Literal["bar", "line", "scatter", "hist", "box", "heatmap"],
    x_col: str,
    y_col: Optional[str] = None,
    hue_col: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
) -> str:
    """Generate a chart for the active dataset and return it as JSON."""

    
    bad = _validate_columns(x_col, y_col, hue_col)
    if bad:
        schema = _get_active_schema()
        return (
            f"ERROR — unknown column(s): {bad}.\n"
            f"Available columns: {schema.get('columns', []) if schema else 'unknown'}"
        )

    try:
        df = _load_df()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_theme(style="whitegrid", palette="muted")

        if chart_type == "bar":
            sns.barplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif chart_type == "line":
            sns.lineplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif chart_type == "scatter":
            sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif chart_type == "hist":
            sns.histplot(data=df, x=x_col, hue=hue_col, kde=True, ax=ax)
        elif chart_type == "box":
            sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
        elif chart_type == "heatmap":
            corr = df.select_dtypes(include="number").corr().round(2)
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        else:
            return f"Unsupported chart_type '{chart_type}'."

        ax.set_title(title or f"{chart_type.capitalize()} — {y_col or x_col} vs {x_col}")
        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=120)
        plt.close(fig)
        encoded = base64.b64encode(buf.getvalue()).decode()
        
        result_json = {
            "type": "visualization",
            "image": encoded,
            "chart_type": chart_type,
            "title": ax.get_title(),
            "summary": summary or f"Generated {chart_type} chart for {y_col or x_col}."
        }
        return json.dumps(result_json)

    except Exception as exc:
        plt.close("all")
        return f"Visualisation error: {exc}"

# Tool 4 — statistical_tool
@tool
def statistical_tool(
    operation: Literal["correlation", "groupby", "value_counts", "describe_column"],
    column: Optional[str] = None,
    group_by: Optional[str] = None,
    agg_func: Literal["mean", "sum", "count", "median", "std", "min", "max"] = "mean",
) -> str:
    """Run a statistical operation on the active dataset."""
    
    
    bad = _validate_columns(column, group_by)
    if bad:
        schema = _get_active_schema()
        return (
            f"ERROR — unknown column(s): {bad}.\n"
            f"Available columns: {schema.get('columns', []) if schema else 'unknown'}"
        )

    try:
        df = _load_df()

        if operation == "correlation":
            result = df.select_dtypes(include="number").corr().round(4)
            return result.to_json()

        if operation == "groupby":
            if not column or not group_by:
                return "ERROR — 'groupby' requires both `column` and `group_by`."
            result = df.groupby(group_by)[column].agg(agg_func).reset_index()
            result.columns = [group_by, f"{agg_func}_{column}"]
            return result.to_json(orient="records", indent=2)

        if operation == "value_counts":
            if not column:
                return "ERROR — 'value_counts' requires `column`."
            vc = df[column].value_counts().head(20)
            return json.dumps(vc.to_dict(), indent=2, default=str)

        if operation == "describe_column":
            if not column:
                return "ERROR — 'describe_column' requires `column`."
            desc = df[column].describe()
            return json.dumps(desc.to_dict(), indent=2, default=str)

        return f"Unknown operation '{operation}'."

    except Exception as exc:
        return f"Statistical error: {exc}"


# Exported tool list (used by the agent node)
ANALYST_TOOLS = [
    dataset_summary_tool,
    pandas_query_tool,
    visualization_tool,
    statistical_tool,
]
