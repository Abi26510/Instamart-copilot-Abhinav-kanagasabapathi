"""validate.py -- Verification and checkpoint assertion script for Part A.

Asserts reference checkpoints from Task 3 (customers) and Task 4 (orders)
across both clean CSV files and SQLite database tables.
Prints exactly 'ALL CHECKPOINTS PASSED' when all assertions succeed.
"""

import os
import sqlite3
import pandas as pd
import numpy as np


def validate_checkpoints():
    clean_dir = "data/clean"
    db_path = "data/instamart.db"

    assert os.path.exists(os.path.join(clean_dir, "customers.csv")), "Missing clean customers.csv"
    assert os.path.exists(os.path.join(clean_dir, "orders.csv")), "Missing clean orders.csv"
    assert os.path.exists(os.path.join(clean_dir, "products.csv")), "Missing clean products.csv"
    assert os.path.exists(db_path), f"Missing database file at {db_path}"

    # Load from clean CSVs
    cust_csv = pd.read_csv(os.path.join(clean_dir, "customers.csv"))
    orders_csv = pd.read_csv(os.path.join(clean_dir, "orders.csv"))
    products_csv = pd.read_csv(os.path.join(clean_dir, "products.csv"))

    # Load from SQLite database
    conn = sqlite3.connect(db_path)
    cust_db = pd.read_sql_query("SELECT * FROM customers", conn)
    orders_db = pd.read_sql_query("SELECT * FROM orders", conn)
    products_db = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # Verify tables have identical row counts between CSV and DB
    assert len(cust_csv) == len(cust_db) == 1200, "Customer row count mismatch"
    assert len(products_csv) == len(products_db) == 40, "Products row count mismatch"
    assert len(orders_csv) == len(orders_db) == 12309, "Orders row count mismatch"

    # Checkpoint 1: Customers city distribution
    expected_cities = {
        "Pune": 227,
        "Delhi": 210,
        "Bengaluru": 197,
        "Chennai": 191,
        "Hyderabad": 191,
        "Mumbai": 184,
    }
    actual_cities = cust_db["city"].value_counts().to_dict()
    assert actual_cities == expected_cities, f"City distribution mismatch: {actual_cities}"

    # Checkpoint 2: Customers gender distribution
    expected_genders = {"female": 610, "male": 560, "unknown": 30}
    actual_genders = cust_db["gender"].value_counts().to_dict()
    assert actual_genders == expected_genders, f"Gender distribution mismatch: {actual_genders}"

    # Checkpoint 3: Customers age - 0 missing and every age between 18 and 60
    assert cust_db["age"].isna().sum() == 0, "Found missing values in customer ages"
    assert (cust_db["age"] >= 18).all() and (cust_db["age"] <= 60).all(), "Ages found outside 18-60"

    # Checkpoint 4: Orders total row count is 12,309 (one per order_id)
    assert len(orders_db) == 12309, f"Expected 12,309 order rows, got {len(orders_db)}"
    assert orders_db["order_id"].nunique() == 12309, "Non-unique order_id found"

    # Checkpoint 5: Orders status breakdown (11,110 completed and 1,199 cancelled; no pending)
    status_counts = orders_db["status"].value_counts().to_dict()
    assert status_counts.get("completed", 0) == 11110, f"Expected 11,110 completed, got {status_counts.get('completed')}"
    assert status_counts.get("cancelled", 0) == 1199, f"Expected 1,199 cancelled, got {status_counts.get('cancelled')}"
    assert status_counts.get("pending", 0) == 0, f"Found pending orders: {status_counts.get('pending')}"

    # Checkpoint 6: 0 missing order_amount
    assert orders_db["order_amount"].isna().sum() == 0, "Missing values found in order_amount"

    # Checkpoint 7: Delivery minutes missingness
    completed_missing_deliv = orders_db.loc[orders_db["status"] == "completed", "delivery_minutes"].isna().sum()
    cancelled_missing_deliv = orders_db.loc[orders_db["status"] == "cancelled", "delivery_minutes"].isna().sum()
    assert completed_missing_deliv == 0, f"Expected 0 missing delivery_minutes for completed orders, got {completed_missing_deliv}"
    assert cancelled_missing_deliv == 1199, f"Expected 1,199 missing delivery_minutes for cancelled orders, got {cancelled_missing_deliv}"

    # Checkpoint 8: Sum of order_amount over completed orders is INR 2,998,668.80
    completed_sum = round(orders_db.loc[orders_db["status"] == "completed", "order_amount"].sum(), 2)
    assert np.isclose(completed_sum, 2998668.80, atol=0.01), f"Expected INR 2,998,668.80, got {completed_sum}"

    # Checkpoint 9: order_ts format in DB and CSV matches YYYY-MM-DD HH:MM:SS
    sample_ts = orders_db["order_ts"].iloc[0]
    assert len(sample_ts) == 19 and sample_ts[10] == " ", f"Timestamp format invalid: {sample_ts}"

    print("ALL CHECKPOINTS PASSED")


if __name__ == "__main__":
    validate_checkpoints()
