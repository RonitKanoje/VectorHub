"""
profiler.py — lightweight dataset profiler.

Called once when a file is uploaded (before the graph runs) to give the
stream_analyst_response function an early-exit check and a cheap profile
stored in state as `dataset_profile`.

This is intentionally NOT a LangGraph node — it runs synchronously outside
the graph so we can validate the file and populate state["dataset_profile"]
before the first SSE chunk is ever sent.  The profile is also shown to the
user immediately as a "file accepted" confirmation message.
"""

from __future__ import annotations

import json

import pandas as pd


def profile_dataset(file_path: str) -> dict:
    """
    Read a CSV or Excel file and return a lightweight metadata profile.

    The profile is stored in AnalystState["dataset_profile"] and surfaced
    to the user as an instant confirmation before the pipeline starts.

    Returns a dict with keys:
        rows, columns, columns_list, numeric_columns, categorical_columns,
        date_columns, missing_values, memory_usage_bytes,
        has_missing  (bool convenience flag),
        missing_pct  (dict col → % missing, only cols with > 0 missing)
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    missing = df.isnull().sum().to_dict()
    total_rows = len(df)

    # Only report columns that actually have missing values
    missing_pct = {
        col: round(count / total_rows * 100, 2)
        for col, count in missing.items()
        if count > 0
    }

    profile = {
        "rows": total_rows,
        "columns": len(df.columns),
        "columns_list": df.columns.tolist(),
        "numeric_columns": int(len(df.select_dtypes(include=["number"]).columns)),
        "categorical_columns": int(len(df.select_dtypes(include=["object", "category"]).columns)),
        "date_columns": int(len(df.select_dtypes(include=["datetime"]).columns)),
        "missing_values": missing,
        "missing_pct": missing_pct,
        "has_missing": bool(missing_pct),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
    }

    return profile


def format_profile_message(profile: dict) -> str:
    """
    Return a short markdown string shown to the user immediately after upload,
    before the pipeline starts processing.
    """
    col_count = profile["columns"]
    row_count = profile["rows"]
    mem_kb = profile["memory_usage_bytes"] // 1024

    lines = [
        f"**Dataset loaded** — {row_count:,} rows × {col_count} columns ({mem_kb:,} KB)",
        f"- Numeric columns: {profile['numeric_columns']}",
        f"- Categorical columns: {profile['categorical_columns']}",
        f"- Date columns: {profile['date_columns']}",
    ]

    if profile["has_missing"]:
        missing_summary = ", ".join(
            f"`{col}` {pct}%" for col, pct in list(profile["missing_pct"].items())[:5]
        )
        if len(profile["missing_pct"]) > 5:
            missing_summary += f" … +{len(profile['missing_pct']) - 5} more"
        lines.append(f"- ⚠️ Missing values in: {missing_summary}")
    else:
        lines.append("- ✅ No missing values detected")

    return "\n".join(lines)
