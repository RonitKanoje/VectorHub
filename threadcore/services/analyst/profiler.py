import pandas as pd
import json

def profile_dataset(file_path: str) -> dict:
    """Read a CSV or Excel file and return metadata/profiling info."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file extension for {file_path}")

    # Calculate basic profile
    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "columns_list": df.columns.tolist(),
        "numeric_columns": len(df.select_dtypes(include=['number']).columns),
        "categorical_columns": len(df.select_dtypes(include=['object', 'category']).columns),
        "date_columns": len(df.select_dtypes(include=['datetime']).columns),
        "missing_values": df.isnull().sum().to_dict(),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum())
    }
    
    return profile
