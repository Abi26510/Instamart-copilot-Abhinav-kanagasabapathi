# Instamart Copilot: Customer Intelligence & Order Analytics

An end-to-end data auditing, cleaning, relational modeling, and customer intelligence analytics pipeline for Instamart quick-commerce operations across six major Indian metropolitan areas.

---

## 1. Numbered Reproduce Guide

Follow these numbered steps to reproduce the entire environment, synthetic data generation, data auditing, cleaning pipeline, checkpoint validations, SQL queries, and exploratory statistical analysis from scratch:

1. **Clone and Navigate to Repository**:
   Ensure you are on the `main` branch:
   ```bash
   git checkout main
   ```

2. **Set Up an Isolated Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Install all pinned libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate Raw Synthetic Data**:
   Executes deterministic data generation creating raw CSV exports and policies:
   ```bash
   python generate_data.py
   ```
   *Output: Populates `data/raw/` with `customers.csv`, `orders.csv`, `products.csv`, `tickets.csv`, `policy_eval.csv`, and `agent_scenarios.csv`.*

5. **Run the Raw Data Audit**:
   Inspects raw dataset schemas, nullability, data anomalies, and verifies audit checkpoints against benchmark references:
   ```bash
   python audit.py
   ```

6. **Clean Datasets and Populate SQLite Database**:
   Applies deterministic cleaning rules, exports clean tables to `data/clean/`, and loads `customers`, `products`, and `orders` into `data/instamart.db`:
   ```bash
   python clean_data.py
   ```

7. **Validate Checkpoints**:
   Runs formal assertions verifying post-cleaning integrity across CSV and SQLite tables:
   ```bash
   python validate.py
   ```
   *Expected output: `ALL CHECKPOINTS PASSED`*

8. **Execute SQL Analysis**:
   Executes the 7 analytical queries stored in `sql/queries.sql` against `data/instamart.db`:
   ```bash
   python run_sql_analysis.py
   ```

9. **Run pandas Cross-Check and Exploratory Analysis**:
   Rebuilds SQL aggregations, computes distribution metrics, fences, correlations, and answers exploratory questions:
   ```bash
   python analysis.py
   ```

---

## 2. Raw Data Audit

The raw data exports represent intentionally dirty quick-commerce operational logs. All three primary tables (`customers.csv`, `orders.csv`, `products.csv`) along with support `tickets.csv` were audited using pandas.

### Summary of Raw Tables

| Table | Rows | Columns | Key Issues Detected |
| :--- | :--- | :--- | :--- |
| `customers.csv` | 1,200 | 5 | Inconsistent casing/whitespace in cities, 10 raw gender variants, 61 missing ages, 6 impossible ages outside 10–100. |
| `orders.csv` | 13,084 | 9 | 119 exact duplicates, 656 unfinalized pending records, 120 unparseable order amounts, 106 negative delivery durations, 2,541 blank delivery times. |
| `products.csv` | 40 | 4 | 0 missing values; complete catalogue across 5 merchandise categories. |
| `tickets.csv` | 164 | 5 | 0 missing values (read with `keep_default_na=False` so empty texts stay empty strings). |

### Column-Level Completeness and Types

- **`customers.csv`**:
  - `customer_id` (str): 0 missing (0.00%)
  - `city` (str): 0 missing (0.00%)
  - `signup_date` (str): 0 missing (0.00%)
  - `age` (float64): 61 missing (5.08%)
  - `gender` (str): 30 missing / blank (2.50%)

- **`orders.csv`**:
  - `order_id` (str): 0 missing (0.00%)
  - `customer_id` (str): 0 missing (0.00%)
  - `product_id` (str): 0 missing (0.00%)
  - `quantity` (int64): 0 missing (0.00%)
  - `order_ts` (str): 0 missing (0.00%)
  - `status` (str): 0 missing (0.00%)
  - `discount_pct` (int64): 0 missing (0.00%)
  - `order_amount` (str): 53 blank missing (0.41%), 120 total unparseable to numeric (0.92%)
  - `delivery_minutes` (float64): 2,541 blank missing (19.42%)

### Target Audit Checkpoints

| Audit Metric | Observed Value | Benchmark Reference | Status |
| :--- | :--- | :--- | :--- |
| Raw `orders.csv` rows | 13,084 | 13,084 | MATCH |
| Number of exact duplicate rows | 119 | 119 | MATCH |
| Number of rows whose status is pending | 656 | 656 | MATCH |
| Number of distinct `order_id` values | 12,309 | 12,309 | MATCH |
| Number of `order_amount` entries that cannot be converted to a number | 120 | 120 | MATCH |
| Number of negative `delivery_minutes` | 106 | 106 | MATCH |
| Number of blank `delivery_minutes` | 2,541 | 2,541 | MATCH |
| `customers.csv`: number of blank age | 61 | 61 | MATCH |
| `customers.csv`: number of age values outside 10–100 | 6 | 6 | MATCH |
| `customers.csv`: number of distinct raw city spellings | 24 | 24 | MATCH |
| `customers.csv`: number of distinct non-blank raw gender spellings | 10 | 10 | MATCH |
| `customers.csv`: number of blank gender | 30 | 30 | MATCH |

---

## 3. Data Cleaning Rules & Impact Documentation

### Clean Customers (`data/clean/customers.csv`)

Cleaning was executed in `clean_data.py` according to the following explicit rules:

1. **Rule C1 — Standardise City**:
   - *Logic*: Trim leading/trailing whitespace and apply Title Case.
   - *Impact*: Standardised **476 malformed city entries** across the 1,200 rows down to exactly 6 valid cities:
     - Pune: 227
     - Delhi: 210
     - Bengaluru: 197
     - Chennai: 191
     - Hyderabad: 191
     - Mumbai: 184

2. **Rule C2 — Normalize Gender**:
   - *Logic*: Map all casing and abbreviation variations to `male`, `female`, or `unknown`. Blanks/nulls map to `unknown`.
   - *Impact*: Modified/standardised **950 values** (including 30 blanks mapped to `unknown`):
     - `female`: 610
     - `male`: 560
     - `unknown`: 30

3. **Rule C3 — Handle Out-of-Range and Missing Age**:
   - *Logic*: Convert age to numeric; treat values `< 10` or `> 100` as missing; impute all missing ages with the median age of the customer's city using `groupby('city')['age'].transform('median')`.
   - *Impact*: Imputed **67 total values** (61 originally blank + 6 biologically impossible ages: 280, -4, 0, 150, 999, 200). After cleaning, there are **0 missing ages**, with all values residing safely between 18.0 and 60.0.

4. **Rule C4 — Datetime Conversion**:
   - *Logic*: Convert `signup_date` from raw string to datetime (`YYYY-MM-DD`).
   - *Impact*: Transformed all **1,200 signup dates**.

---

### Clean Orders (`data/clean/orders.csv`)

Order records were processed in strictly enforced sequential order:

1. **Rule O1 — Timestamp Standardization**:
   - *Logic*: Parse `order_ts` into a standard datetime object.
   - *Impact*: Converted all **13,084 timestamp strings**.

2. **Rule O2 — Exact Duplicate Removal**:
   - *Logic*: Deduplicate fully identical rows across all columns.
   - *Impact*: Purged exactly **119 duplicate rows**, reducing total rows from 13,084 to 12,965.

3. **Rule O3 — Resolve Order Status Lifecycles**:
   - *Logic*: Many orders contained an initial `pending` record followed by a subsequent `completed` or `cancelled` update. For each `order_id`, records were ordered by `order_ts` ascending and only the latest record was retained (`drop_duplicates(subset=['order_id'], keep='last')`).
   - *Impact*: Eliminated **656 obsolete pending records**, leaving exactly **12,309 unique orders** (11,110 completed and 1,199 cancelled; 0 pending).

4. **Rule O4 — Order Amount Coercion and Catalog Price Imputation**:
   - *Logic*: Coerce `order_amount` to numeric (forcing non-numeric strings to NaN). Join with `products` on `product_id` and impute missing amounts using:
     $$\text{order\_amount} = \text{round}\left(\text{price\_inr} \times \text{quantity} \times \left(1 - \frac{\text{discount\_pct}}{100}\right), 2\right)$$
   - *Impact*: Imputed **112 missing/corrupted order amounts** (53 blank + 59 non-numeric strings). Post-cleaning, missing `order_amount` count is **0**.

5. **Rule O5 — Delivery Time Validation and Category-Median Imputation**:
   - *Logic*: Treat negative `delivery_minutes` as missing (set to NaN). For `completed` orders, impute missing delivery durations with the median delivery time of that product category among completed orders via `groupby('category')['delivery_minutes'].transform('median')`. For `cancelled` orders, preserve `delivery_minutes` as missing (NaN) since cancelled orders were never delivered.
   - *Impact*:
     - **105 negative delivery durations** in the deduplicated table were reset to NaN.
     - **774 completed orders** with missing/negative durations were imputed via product category medians.
     - **0 missing delivery minutes** remain among completed orders.
     - Exactly **1,199 cancelled orders** retain missing delivery minutes.
     - Total completed order revenue is exactly **INR 2,998,668.80**.

---

## 4. SQLite Database Architecture

Clean tables are stored in SQLite database at `data/instamart.db`:
- **`customers`**: `customer_id`, `city`, `signup_date`, `age`, `gender` (1,200 rows).
- **`products`**: `product_id`, `product_name`, `category`, `price_inr` (40 rows).
- **`orders`**: `order_id`, `customer_id`, `product_id`, `quantity`, `order_ts`, `status`, `discount_pct`, `order_amount`, `delivery_minutes` (12,309 rows).
  - Note: `order_ts` is stored as text formatted as `YYYY-MM-DD HH:MM:SS`.

---

## 5. SQL Analysis Queries & Findings

All queries are maintained in [`sql/queries.sql`](file:///A:/Capstone%20project/instamart-copilot/sql/queries.sql) and executed via [`run_sql_analysis.py`](file:///A:/Capstone%20project/instamart-copilot/run_sql_analysis.py).

### Q1 — Filtering and Aggregation (`WHERE` then `HAVING`)
- **Objective**: Identify high-value customers with substantial individual completed transactions (> INR 500) whose aggregate spend across those specific high-value orders exceeds INR 8,000.
- **Result**: Exactly **30 customers** qualify.
- **Top 3 Customers**:
  1. `C0693`: INR 13,776.55
  2. `C0082`: INR 12,317.70
  3. `C0743`: INR 12,266.85

### Q2 — Three-Table Join (Revenue by City & Category)
- **Objective**: Calculate total completed revenue segmented across all city and product category combinations by joining `orders`, `customers`, and `products`.
- **Result**: Exactly **30 rows** (6 cities × 5 categories).
- **Total Revenue**: Sum of all 30 cells equals **INR 2,998,668.80**.
- **Top Cell**: **Bengaluru / Electronics** at **INR 233,909.45**.

### Q3 — Scalar Subquery
- **Objective**: Retrieve catalogue products priced strictly above the average catalogue price (catalogue average = INR 289.32).
- **Result**: Exactly **11 products** (led by Bluetooth Speaker at INR 1,999 and Wireless Earbuds at INR 1,499).

### Q4 — Outer Join (`LEFT JOIN`)
- **Objective**: Identify inactive or non-converting customers who have zero completed orders.
- **Result**: Exactly **25 customers** have never completed an order.

### Q5 — Common Table Expressions (CTE)
- **Objective**: Compute customer-level completed spend via one CTE, calculate the average customer total across all active customers in a second CTE (average = INR 2,552.06), and return customers exceeding this benchmark.
- **Result**: Exactly **550 customers** spend above the mean customer spend.

### Q6 — Ranking Window Functions (`RANK`, `DENSE_RANK`, `ROW_NUMBER`)
- **Objective**: Rank customer spend partitioned by city using window functions ordered by total spend descending.
- **Top Customer per City**:
  - Bengaluru: `C0082` (INR 12,856.20)
  - Chennai: `C0930` (INR 10,151.40)
  - Delhi: `C0291` (INR 13,742.60)
  - Hyderabad: `C0743` (INR 12,730.05)
  - Mumbai: `C0693` (INR 14,766.55)
  - Pune: `C0426` (INR 10,377.10)
- **Rank Discrepancy Count**: Exactly **8 rows** exhibit `RANK()` different from `ROW_NUMBER()`.
- **Reason for Discrepancy**:
  > Ties cause `RANK()` to assign identical ranks to customers sharing the exact same completed spend within a city partition and skip subsequent rank numbers by the number of tied rows, whereas `ROW_NUMBER()` assigns strictly sequential, distinct integers arbitrarily resolving ties based on row scan order.

### Q7 — Running Total
- **Objective**: Compute daily completed revenue with an expanding window cumulative sum ordered chronologically by calendar day.
- **Result**: Exactly **183 daily rows** (2025-04-01 through 2025-09-30).
- **Final Cumulative Revenue**: Exactly **INR 2,998,668.80**.

---

## 6. pandas Cross-Check and Exploratory Data Analysis

### (a) Cross-Check with `pd.pivot_table` and Named Aggregations

Rebuilding Q2 in pandas produces identical revenue figures:
- **Grand Total**: **INR 2,998,668.80** (matching SQL total).

#### City-Level Completed Order Summary

| City | Total Spend (INR) | Mean Order Value (INR) | Completed Orders |
| :--- | :--- | :--- | :--- |
| **Bengaluru** | 523,643.40 | 276.47 | 1,894 |
| **Chennai** | 463,629.15 | 272.72 | 1,700 |
| **Delhi** | 502,829.80 | 243.62 | 2,064 |
| **Hyderabad** | 528,589.90 | 284.95 | 1,855 |
| **Mumbai** | 479,058.50 | 297.00 | 1,613 |
| **Pune** | 500,918.05 | 252.48 | 1,984 |

### (b) Order Amount Distribution & Outlier Analysis

- **Mean**: INR 269.91
- **Median**: INR 135.00
- **Skewness**: 4.6088 (strongly right-skewed)
- **First Quartile ($Q_1$)**: INR 64.80
- **Third Quartile ($Q_3$)**: INR 297.00
- **Interquartile Range ($IQR$)**: INR 232.20
- **Lower Fence ($Q_1 - 1.5 \times IQR$)**: INR -283.50 (Outliers Below: 0)
- **Upper Fence ($Q_3 + 1.5 \times IQR$)**: INR 645.30 (Outliers Above: 897)

### Correlation Matrix (Completed Orders)

| Variable | `order_amount` | `discount_pct` | `quantity` | `delivery_minutes` |
| :--- | :--- | :--- | :--- | :--- |
| **`order_amount`** | 1.0000 | -0.0951 | 0.0873 | -0.0031 |
| **`discount_pct`** | -0.0951 | 1.0000 | -0.0004 | -0.0098 |
| **`quantity`** | 0.0873 | -0.0004 | 1.0000 | -0.0126 |
| **`delivery_minutes`** | -0.0031 | -0.0098 | -0.0126 | 1.0000 |

The pair with the largest correlation in absolute value is **`order_amount` with `discount_pct` at $r \approx -0.0951$** (slightly exceeding `order_amount` and `quantity` at $r \approx +0.0873$).

---

### Four Exploratory Questions (173 Words Total)

1. **What is this data about?**  
   It captures quick-commerce transactions across six Indian metropolitan cities, tracking 1,200 customers, 40 catalog items across five categories, order fulfillment timelines, discounts, and customer spend.

2. **What do its distributions and statistics look like?**  
   Completed `order_amount` is heavily right-skewed (skewness ~ 4.61), where the mean (INR 269.91) is double the median (INR 135.00), driven by occasional high-ticket electronics purchases compared to frequent, low-cost grocery and dairy staples.

3. **Are there outliers or anomalies?**  
   Using the 1.5xIQR rule ($Q_1$ = INR 64.80, $Q_3$ = INR 297.00, upper fence = INR 645.30), there are 897 high-value outliers above the upper fence and 0 below. These represent legitimate multi-item or premium electronics orders rather than data corruption.

4. **What relationships exist between variables?**  
   The largest correlation in absolute value is between `order_amount` and `discount_pct` at $r \approx -0.095$, slightly exceeding `order_amount` and `quantity` at $r \approx +0.087$. These near-zero associations indicate that order amounts, discounting, and fulfillment times vary independently. Crucially, a correlation of this size does not establish causation.
