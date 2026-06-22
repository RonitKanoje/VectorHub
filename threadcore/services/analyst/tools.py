import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from langchain_core.tools import tool

# Simple state variable to hold the current active dataset path
_current_dataset_path = None

def set_current_dataset(path: str):
    global _current_dataset_path
    _current_dataset_path = path

def _load_df() -> pd.DataFrame:
    global _current_dataset_path
    if not _current_dataset_path or not os.path.exists(_current_dataset_path):
        raise ValueError("No active dataset loaded.")
    if _current_dataset_path.endswith('.csv'):
        return pd.read_csv(_current_dataset_path)
    return pd.read_excel(_current_dataset_path)

@tool
def dataset_summary_tool() -> str:
    """Returns basic statistical summary and data types of the dataset."""
    df = _load_df()
    summary = df.describe(include='all').to_string()
    dtypes = df.dtypes.to_string()
    return f"Data Types:\n{dtypes}\n\nStatistical Summary:\n{summary}"

@tool
def pandas_query_tool(query: str) -> str:
    """
    Executes a simple pandas string query. 
    Pass a string that is valid for df.query(query).
    """
    df = _load_df()
    try:
        result = df.query(query)
        return result.to_string()
    except Exception as e:
        return f"Error executing query: {e}"

@tool
def visualization_tool(chart_type: str, x_col: str, y_col: str = None) -> str:
    """
    Generates a chart and returns it as a base64 encoded image string.
    chart_type should be one of: 'bar', 'line', 'scatter', 'hist'
    x_col is the column name for the x-axis.
    y_col is the column name for the y-axis (optional for hist).
    """
    df = _load_df()
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")
    
    try:
        if chart_type == 'bar':
            sns.barplot(data=df, x=x_col, y=y_col)
        elif chart_type == 'line':
            sns.lineplot(data=df, x=x_col, y=y_col)
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x=x_col, y=y_col)
        elif chart_type == 'hist':
            sns.histplot(data=df, x=x_col)
        else:
            return "Unsupported chart type."
            
        plt.title(f"{chart_type.capitalize()} Plot of {y_col if y_col else ''} vs {x_col}")
        plt.tight_layout()
        
        # Save to base64
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"![Chart](data:image/png;base64,{encoded})"
    except Exception as e:
        return f"Error generating chart: {e}"
