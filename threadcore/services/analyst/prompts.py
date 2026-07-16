from typing import Any


def build_schema_system_prompt(schema: dict[str, Any]) -> str:
 
    col_lines = "\n".join(
        f"{col} ({schema['dtypes'].get(col, '?')})  "
        f"nulls={schema['null_counts'].get(col, 0)}  "
        f"samples={schema['sample_values'].get(col, [])}"
        for col in schema["columns"]
    )
    
    return (
        "You are a senior data analyst with access to four tools:\n"
        "  dataset_summary_tool  — full describe + dtypes + null counts\n"
        "  pandas_query_tool     — filter rows with df.query()\n"
        "  visualization_tool    — generate charts (bar/line/scatter/hist/box/heatmap)\n"
        "  statistical_tool      — correlation / groupby / value_counts / describe_column\n\n"
        "DATASET SCHEMA (authoritative — never invent column names):\n"
        f"  Shape: {schema['shape']['rows']} rows × {schema['shape']['cols']} cols\n"
        f"{col_lines}\n\n"
        "Rules:\n"
        "  1. ONLY use column names listed above.\n"
        "  2. Call dataset_summary_tool first if the user asks a broad question.\n"
        "  3. Always call at least one tool before writing the final answer.\n"
        "  4. Return a clear, markdown-formatted answer after you have gathered data.\n"
        "  5. When you call visualization_tool, the chart will be displayed automatically.\n"
        "     Do NOT include any image tags or base64 data in your text response.\n"
        "     Simply describe the chart in words (e.g. 'I generated a bar chart of X vs Y.').\n"
        "  6. Never output base64 strings or image data — charts are rendered separately.\n"
    )


# Synthesis Agent Prompts

SYNTHESIS_SYSTEM_PROMPT = (
    "You are a senior data analyst.\n"
    "The tool-use agent provided only a brief or empty answer.\n"
    "Use the preprocessing report and EDA report below to write a "
    "comprehensive markdown analysis covering: data quality, key statistics, "
    "distributions, outliers, correlations, and recommendations.\n"
    "Do NOT invent statistics. Only report what the reports contain."
)

def build_synthesis_human_prompt(agent_answer: str, preprocessing_report: str, eda_report: str) -> str:
 
    return (
        f"AGENT ANSWER (expand on this):\n{agent_answer}\n\n"
        f"PREPROCESSING REPORT:\n{preprocessing_report[:4000]}\n\n"
        f"EDA REPORT:\n{eda_report[:4000]}"
    )
