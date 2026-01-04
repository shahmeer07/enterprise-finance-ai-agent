import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/Enhanced_Invoices_5000.xlsx")


def get_overdue_invoices(minimum_days_overdue=0, limit=10):
    # Read Excel properly
    df = pd.read_excel(DATA_PATH)

    # Normalize column names (important)
    df.columns = df.columns.str.lower()

    # Ensure required column exists
    if "days_overdue" not in df.columns:
        raise ValueError("Column 'days_overdue' not found in invoice dataset")

    # Filter overdue invoices
    overdue_df = df[df["days_overdue"] >= minimum_days_overdue]

    # Sort by most overdue first (recommended)
    overdue_df = overdue_df.sort_values(
        by="days_overdue",
        ascending=False
    )

    # Limit results
    overdue_df = overdue_df.head(limit)

    # Convert to list of dicts (agent-friendly)
    return overdue_df.to_dict(orient="records")
