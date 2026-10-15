"""run_sql_analysis.py -- Executes SQL queries in sql/queries.sql against data/instamart.db.

Runs Q1 through Q7 with pandas.read_sql_query and prints the results
matching all reference specifications.
"""

import sqlite3
import pandas as pd
import numpy as np


def run_queries(db_path: str = "data/instamart.db"):
    conn = sqlite3.connect(db_path)

    print("=" * 80)
    print("INSTAMART SQL ANALYSIS (data/instamart.db)")
    print("=" * 80)

    # Q1: WHERE then HAVING
    q1 = """
    SELECT 
        customer_id, 
        ROUND(SUM(order_amount), 2) AS total_amount
    FROM orders
    WHERE status = 'completed' AND order_amount > 500
    GROUP BY customer_id
    HAVING SUM(order_amount) > 8000
    ORDER BY total_amount DESC;
    """
    df_q1 = pd.read_sql_query(q1, conn)
    print(f"\n[Q1] WHERE then HAVING (Completed orders > 500, customer total > 8000)")
    print(f"Customer Count: {len(df_q1)} (Reference: 30)")
    print("Top 5 Customers:")
    print(df_q1.head().to_string(index=False))

    # Q2: Three-table join
    q2 = """
    SELECT 
        c.city, 
        p.category, 
        ROUND(SUM(o.order_amount), 2) AS revenue
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'completed'
    GROUP BY c.city, p.category
    ORDER BY c.city, p.category;
    """
    df_q2 = pd.read_sql_query(q2, conn)
    total_rev = round(df_q2["revenue"].sum(), 2)
    max_cell = df_q2.loc[df_q2["revenue"].idxmax()]
    print(f"\n[Q2] Three-Table Join (Revenue by City and Product Category)")
    print(f"Row Count: {len(df_q2)} (Reference: 30)")
    print(f"Total Revenue across 30 cells: INR {total_rev:,.2f} (Reference: INR 2,998,668.80)")
    print(f"Largest cell: {max_cell['city']} / {max_cell['category']} at INR {max_cell['revenue']:,.2f} (Reference: Bengaluru / Electronics at INR 233,909.45)")

    # Q3: Scalar subquery
    q3 = """
    SELECT 
        product_id, 
        product_name, 
        category, 
        price_inr
    FROM products
    WHERE price_inr > (SELECT AVG(price_inr) FROM products)
    ORDER BY price_inr DESC;
    """
    df_q3 = pd.read_sql_query(q3, conn)
    cat_avg = pd.read_sql_query("SELECT AVG(price_inr) as avg_p FROM products", conn)["avg_p"].iloc[0]
    print(f"\n[Q3] Scalar Subquery (Products priced above average catalogue price INR {cat_avg:.2f})")
    print(f"Product Count: {len(df_q3)} (Reference: 11)")
    print(df_q3.to_string(index=False))

    # Q4: LEFT JOIN
    q4 = """
    SELECT 
        c.customer_id, 
        c.city, 
        c.signup_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    WHERE o.order_id IS NULL
    ORDER BY c.customer_id;
    """
    df_q4 = pd.read_sql_query(q4, conn)
    print(f"\n[Q4] LEFT JOIN (Customers who have no completed order)")
    print(f"Customer Count: {len(df_q4)} (Reference: 25)")
    print("First 5 customers with 0 completed orders:")
    print(df_q4.head().to_string(index=False))

    # Q5: CTE
    q5 = """
    WITH customer_spend AS (
        SELECT 
            customer_id, 
            SUM(order_amount) AS total_spend
        FROM orders
        WHERE status = 'completed'
        GROUP BY customer_id
    ),
    avg_spend AS (
        SELECT 
            AVG(total_spend) AS overall_avg
        FROM customer_spend
    )
    SELECT 
        cs.customer_id, 
        ROUND(cs.total_spend, 2) AS total_spend
    FROM customer_spend cs
    CROSS JOIN avg_spend av
    WHERE cs.total_spend > av.overall_avg
    ORDER BY cs.total_spend DESC;
    """
    df_q5 = pd.read_sql_query(q5, conn)
    avg_spend_val = pd.read_sql_query(
        "WITH cs AS (SELECT customer_id, SUM(order_amount) AS s FROM orders WHERE status='completed' GROUP BY customer_id) SELECT AVG(s) as a FROM cs",
        conn
    )["a"].iloc[0]
    print(f"\n[Q5] Common Table Expression (Customers spending above average completed spend)")
    print(f"Customer Count: {len(df_q5)} (Reference: 550)")
    print(f"Average Completed Spend: INR {avg_spend_val:.2f} (Reference: INR 2,552.06)")

    # Q6: Ranking window functions
    q6 = """
    WITH cust_spend AS (
        SELECT 
            c.customer_id, 
            c.city, 
            ROUND(SUM(o.order_amount), 2) AS total_spend
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status = 'completed'
        GROUP BY c.customer_id, c.city
    )
    SELECT 
        customer_id, 
        city, 
        total_spend,
        RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS rnk,
        DENSE_RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS dense_rnk,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spend DESC) AS row_num
    FROM cust_spend
    ORDER BY city, total_spend DESC;
    """
    df_q6 = pd.read_sql_query(q6, conn)
    top_per_city = df_q6[df_q6["rnk"] == 1].sort_values("city")
    diff_count = (df_q6["rnk"] != df_q6["row_num"]).sum()
    print(f"\n[Q6] Ranking Window Functions (OVER Partition by City ORDER BY total_spend DESC)")
    print("Top customer per city:")
    for _, r in top_per_city.iterrows():
        print(f"  - {r['city']}: {r['customer_id']} (INR {r['total_spend']:,.2f})")
    print(f"Rows where RANK() != ROW_NUMBER(): {diff_count} (Reference: 8)")

    # Q7: Running total
    q7 = """
    WITH daily_rev AS (
        SELECT 
            SUBSTR(order_ts, 1, 10) AS day, 
            ROUND(SUM(order_amount), 2) AS revenue
        FROM orders
        WHERE status = 'completed'
        GROUP BY SUBSTR(order_ts, 1, 10)
    )
    SELECT 
        day, 
        revenue,
        ROUND(SUM(revenue) OVER (ORDER BY day), 2) AS cumulative_revenue
    FROM daily_rev
    ORDER BY day;
    """
    df_q7 = pd.read_sql_query(q7, conn)
    last_cum = df_q7["cumulative_revenue"].iloc[-1]
    print(f"\n[Q7] Running Total (Daily completed revenue with cumulative SUM OVER ORDER BY day)")
    print(f"Daily Rows Count: {len(df_q7)} (Reference: 183)")
    print(f"Final Cumulative Revenue: INR {last_cum:,.2f} (Reference: INR 2,998,668.80)")

    conn.close()


if __name__ == "__main__":
    run_queries()
