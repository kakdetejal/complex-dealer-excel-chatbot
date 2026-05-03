import re
import pandas as pd


def detect_month_columns(df):

    pattern = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"

    month_cols = [
        col for col in df.columns
        if re.search(pattern, str(col).lower())
    ]

    #  fallback
    if not month_cols:
        return df.select_dtypes(include=['number']).columns.tolist()

    return month_cols