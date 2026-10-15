"""audit.py -- Audit raw data tables before cleaning.

Reports:
- Table shapes, column dtypes, missing value counts & percentages for customers, orders, products.
- Specific audit metrics table compared against reference values.
"""

import pandas as pd
import numpy as np


def run_audit(raw_dir: str = "data/raw"):
    customers = pd.read_csv(f"{raw_dir}/customers.csv")
    orders = pd.read_csv(f"{raw_dir}/orders.csv")
    products = pd.read_csv(f"{raw_dir}/products.csv")
    # Read tickets.csv with keep_default_na=False as requested
    tickets = pd.read_csv(f"{raw_dir}/tickets.csv", keep_default_na=False)

    tables = {
        "customers.csv": customers,
        "orders.csv": orders,
        "products.csv": products,
        "tickets.csv": tickets,
    }

    print("=" * 80)
    print("RAW DATASET SUMMARY AUDIT")
    print("=" * 80)
    for name, df in tables.items():
        print(f"\n--- {name} (Shape: {df.shape[0]} rows, {df.shape[1]} columns) ---")
        col_summary = []
        for col in df.columns:
            if name == "tickets.csv" and col == "text":
                missing = (df[col].astype(str).str.strip() == "").sum()
            else:
                missing = df[col].isna().sum()
            pct = (missing / len(df)) * 100
            col_summary.append({
                "Column": col,
                "Dtype": str(df[col].dtype),
                "Missing Count": missing,
                "Missing Pct": f"{pct:.2f}%"
            })
        print(pd.DataFrame(col_summary).to_string(index=False))

    print("\n" + "=" * 80)
    print("TARGET AUDIT METRICS TABLE")
    print("=" * 80)

    # Orders checks
    raw_orders_rows = len(orders)
    exact_dupes = orders.duplicated().sum()
    pending_rows = (orders["status"] == "pending").sum()
    distinct_orders = orders["order_id"].nunique()
    numeric_amounts = pd.to_numeric(orders["order_amount"], errors="coerce")
    non_numeric_amounts = numeric_amounts.isna().sum()
    deliv_numeric = pd.to_numeric(orders["delivery_minutes"], errors="coerce")
    neg_deliv = (deliv_numeric < 0).sum()
    blank_deliv = orders["delivery_minutes"].isna().sum()

    # Customers checks
    blank_age = customers["age"].isna().sum()
    age_numeric = pd.to_numeric(customers["age"], errors="coerce")
    outside_age = ((age_numeric < 10) | (age_numeric > 100)).sum()
    raw_city_spellings = customers["city"].nunique()
    nonblank_genders = customers["gender"].dropna().loc[lambda s: s.astype(str).str.strip() != ""]
    distinct_raw_gender = nonblank_genders.nunique()
    blank_gender = customers["gender"].isna().sum() + (customers["gender"].astype(str).str.strip() == "").sum()

    metrics = [
        ("raw orders.csv rows", raw_orders_rows, 13084),
        ("number of exact duplicate rows", exact_dupes, 119),
        ("number of rows whose status is pending", pending_rows, 656),
        ("number of distinct order_id values", distinct_orders, 12309),
        ("number of order_amount entries that cannot be converted to a number", non_numeric_amounts, 120),
        ("number of negative delivery_minutes", neg_deliv, 106),
        ("number of blank delivery_minutes", blank_deliv, 2541),
        ("customers.csv: number of blank age", blank_age, 61),
        ("customers.csv: number of age values outside 10-100", outside_age, 6),
        ("customers.csv: number of distinct raw city spellings", raw_city_spellings, 24),
        ("customers.csv: number of distinct non-blank raw gender spellings", distinct_raw_gender, 10),
        ("customers.csv: number of blank gender", blank_gender, 30),
    ]

    df_metrics = pd.DataFrame(metrics, columns=["Audit Metric", "Observed Value", "Reference Value"])
    df_metrics["Status"] = np.where(df_metrics["Observed Value"] == df_metrics["Reference Value"], "MATCH", "MISMATCH")
    print(df_metrics.to_string(index=False))

    all_matched = (df_metrics["Status"] == "MATCH").all()
    print("\nOverall Raw Audit Result:", "ALL METRICS MATCHED" if all_matched else "MISMATCH DETECTED")
    return df_metrics


if __name__ == "__main__":
    run_audit()
