import json
import numpy as np
import pandas as pd
from typing import Any


def coerce_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    
    log = []
    for col in df.select_dtypes(include="object").columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        success_rate = converted.notna().mean()
        if success_rate >= 0.8:  # 80%+ values are numeric → cast
            df[col] = converted
            log.append({
                "column": col,
                "action": "coerced_to_numeric",
                "success_rate": round(float(success_rate), 3),
            })
    return df, log


def analyse_missing(df: pd.DataFrame) -> list[dict]:
   
    report = []
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        if n_missing == 0:
            continue
        pct = round(n_missing / len(df) * 100, 2)
        dtype = str(df[col].dtype)
        if pct > 50:
            strategy = "drop_column"
        elif df[col].dtype in [np.float64, np.int64, float, int]:
            strategy = "fill_median"
            df[col] = df[col].fillna(df[col].median())
        else:
            strategy = "fill_mode"
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])

        report.append({
            "column": col,
            "missing_count": n_missing,
            "missing_pct": pct,
            "dtype": dtype,
            "strategy_applied": strategy,
        })
    return report


def detect_outliers(df: pd.DataFrame) -> list[dict]:
    
    report = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        if len(outliers) > 0:
            report.append({
                "column": col,
                "outlier_count": int(len(outliers)),
                "outlier_pct": round(len(outliers) / len(df) * 100, 2),
                "lower_fence": round(float(lower), 4),
                "upper_fence": round(float(upper), 4),
                "min_val": round(float(df[col].min()), 4),
                "max_val": round(float(df[col].max()), 4),
            })
    return report


def run_preprocessing(file_path: str) -> tuple[pd.DataFrame, str]:
  
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, encoding="latin1")
    else:
        df = pd.read_excel(file_path)

    original_shape = df.shape

    df, coerce_log = coerce_types(df)
    missing_report = analyse_missing(df)
    outlier_report = detect_outliers(df)

    report: dict[str, Any] = {
        "original_shape": {"rows": original_shape[0], "cols": original_shape[1]},
        "final_shape": {"rows": len(df), "cols": len(df.columns)},
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "coercions_applied": coerce_log,
        "missing_values": missing_report,
        "outliers_detected": outlier_report,
    }

    return df, json.dumps(report, indent=2)
