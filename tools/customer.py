import pandas as pd
from pathlib import Path

CUSTOMER_PATH = Path("data/CustomerData.xlsx")


def get_customer_by_id(customer_id):
    df = pd.read_excel(CUSTOMER_PATH)
    df.columns = df.columns.str.lower()

    if "customer_id" not in df.columns:
        raise ValueError("customer_id column missing in CustomerData")

    match = df[df["customer_id"] == customer_id]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def get_customer_email(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None

    return customer.get("email")
