"""clean_data.py -- Data cleaning pipeline for Instamart Customer Intelligence.

Audits and cleans raw datasets (customers.csv, orders.csv, products.csv),
persists the cleaned datasets to data/clean/*.csv, and populates data/instamart.db.
"""

import os
import sqlite3
import pandas as pd
import numpy as np


def clean_customers(raw_dir: str = "data/raw") -> pd.DataFrame:
    """Clean customers table according to specified rules:
    (a) Standardise city by trimming whitespace and applying title case (6 cities).
    (b) Map gender spelling to male, female, or unknown (blank -> unknown).
    (c) Treat ages outside 10-100 as missing, fill missing with city median age.
    (d) Convert signup_date to datetime.
    """
    cust_path = os.path.join(raw_dir, "customers.csv")
    cust = pd.read_csv(cust_path)

    # (a) Standardise city: strip whitespace and title-case
    cust["city"] = cust["city"].astype(str).str.strip().str.title()

    # (b) Map gender: male, female, unknown
    def normalize_gender(val):
        if pd.isna(val) or str(val).strip() == "":
            return "unknown"
        g = str(val).strip().lower()
        if g in ["male", "m"]:
            return "male"
        elif g in ["female", "f"]:
            return "female"
        return "unknown"

    cust["gender"] = cust["gender"].apply(normalize_gender)

    # (c) Age: treat < 10 or > 100 as missing, fill with city median
    cust["age"] = pd.to_numeric(cust["age"], errors="coerce")
    cust.loc[(cust["age"] < 10) | (cust["age"] > 100), "age"] = np.nan
    city_medians = cust.groupby("city")["age"].transform("median")
    cust["age"] = cust["age"].fillna(city_medians)

    # (d) Convert signup_date to datetime
    cust["signup_date"] = pd.to_datetime(cust["signup_date"])

    return cust


def clean_orders(raw_dir: str = "data/raw", products_df: pd.DataFrame = None) -> pd.DataFrame:
    """Clean orders table in explicit, documented order:
    1. Convert order_ts to datetime.
    2. Remove exact duplicate rows.
    3. Keep only the record with the latest order_ts for each order_id.
    4. Convert order_amount to numeric; fill missing using product price:
       round(price_inr * quantity * (1 - discount_pct / 100), 2)
    5. Set negative delivery_minutes to missing (NaN).
       For completed orders, impute missing delivery_minutes with median delivery
       time of that product category among completed orders.
       For cancelled orders, leave delivery_minutes as missing (NaN).
    """
    orders_path = os.path.join(raw_dir, "orders.csv")
    orders = pd.read_csv(orders_path)

    if products_df is None:
        products_df = pd.read_csv(os.path.join(raw_dir, "products.csv"))

    # Rule 1: Convert order_ts to datetime
    orders["order_ts"] = pd.to_datetime(orders["order_ts"])

    # Rule 2: Remove exact duplicate rows
    orders = orders.drop_duplicates()

    # Rule 3: Keep latest order_ts per order_id
    orders = orders.sort_values(by=["order_id", "order_ts"]).drop_duplicates(
        subset=["order_id"], keep="last"
    )

    # Rule 4: Convert order_amount to numeric, impute unparseable/missing from product catalog
    orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")
    orders = orders.merge(
        products_df[["product_id", "category", "price_inr"]],
        on="product_id",
        how="left",
    )
    imputed_amounts = (
        orders["price_inr"]
        * orders["quantity"]
        * (1 - orders["discount_pct"] / 100.0)
    ).round(2)
    orders["order_amount"] = orders["order_amount"].fillna(imputed_amounts)

    # Rule 5: Negative delivery_minutes to NaN; impute completed orders by category median; keep cancelled NaN
    orders["delivery_minutes"] = pd.to_numeric(orders["delivery_minutes"], errors="coerce")
    orders.loc[orders["delivery_minutes"] < 0, "delivery_minutes"] = np.nan

    completed_mask = orders["status"] == "completed"
    cat_medians = orders[completed_mask].groupby("category")["delivery_minutes"].transform("median")
    orders.loc[completed_mask, "delivery_minutes"] = orders.loc[
        completed_mask, "delivery_minutes"
    ].fillna(cat_medians)

    # Retain strictly the standard order columns
    ordered_cols = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "order_ts",
        "status",
        "discount_pct",
        "order_amount",
        "delivery_minutes",
    ]
    return orders[ordered_cols].sort_values("order_id").reset_index(drop=True)


def main():
    raw_dir = "data/raw"
    clean_dir = "data/clean"
    db_path = "data/instamart.db"

    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print("Cleaning products...")
    products = pd.read_csv(os.path.join(raw_dir, "products.csv"))
    products.to_csv(os.path.join(clean_dir, "products.csv"), index=False)

    print("Cleaning customers...")
    customers = clean_customers(raw_dir=raw_dir)
    # Save CSV with signup_date as YYYY-MM-DD
    customers_csv = customers.copy()
    customers_csv["signup_date"] = customers_csv["signup_date"].dt.strftime("%Y-%m-%d")
    customers_csv.to_csv(os.path.join(clean_dir, "customers.csv"), index=False)

    print("Cleaning orders...")
    orders = clean_orders(raw_dir=raw_dir, products_df=products)
    # Format order_ts as YYYY-MM-DD HH:MM:SS for CSV and SQLite
    orders_export = orders.copy()
    orders_export["order_ts"] = orders_export["order_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    orders_export.to_csv(os.path.join(clean_dir, "orders.csv"), index=False)

    print(f"Writing to SQLite database {db_path}...")
    conn = sqlite3.connect(db_path)
    try:
        customers_csv.to_sql("customers", conn, if_exists="replace", index=False)
        products.to_sql("products", conn, if_exists="replace", index=False)
        orders_export.to_sql("orders", conn, if_exists="replace", index=False)
    finally:
        conn.close()

    print("Data cleaning completed successfully.")
    print(f"Clean CSVs: {clean_dir}/")
    print(f"SQLite DB: {db_path}")


if __name__ == "__main__":
    main()
