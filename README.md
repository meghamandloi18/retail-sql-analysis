# Retail Sales Analysis (SQL)

A normalized retail sales database (customers, products, orders) analyzed with SQL — joins, aggregations, and window functions — to answer common business questions: which products/regions drive revenue, how sales trend month over month, and which customers are highest-value or at risk of churn.

## Schema
- `customers (customer_id, customer_name, region, signup_date)`
- `products (product_id, product_name, category, unit_price)`
- `orders (order_id, customer_id, product_id, order_date, quantity)`

150 customers, 13 products across 4 categories, 4,000 orders spanning 2 years.

## Key queries (see `queries.sql` for all 10, fully commented)
1. Revenue by product category
2. Top 5 best-selling products
3. Revenue by region
4. Monthly revenue trend
5. Month-over-month revenue growth % (`LAG()` window function)
6. Top 10 customers by lifetime spend
7. Top 3 customers per region (`RANK()` window function)
8. Average order value by category
9. Customers with no orders in the last 90 days (churn-risk flag)
10. Cumulative revenue over time (running total window function)

## Sample findings
- **Apparel is the top revenue category** (~$91.3K), driven by Running Shoes and Denim Jacket, despite Electronics having the most units sold.
- **Revenue is fairly balanced across regions**, with West (~$61.2K) and East (~$60.0K) slightly ahead of North and South.
- **Apparel has the highest average order value** (~$100.6) — over 4x Grocery's AOV (~$22.5) — suggesting different cart-building strategies by category.
- Window functions (`LAG`, `RANK`, running `SUM`) were used to compute month-over-month growth, per-region customer rankings, and cumulative revenue without extra self-joins.

## Tech stack
SQLite · SQL (joins, CTEs, window functions) · Python (for data generation)

## Live demo
Deployed on Streamlit Community Cloud: (https://retail-sql-analysis-3jlvmfmtxvyudfhjf6fuh3.streamlit.app)

Run locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## How to run the raw queries
```bash
python generate_data.py          # creates retail_sales.db
sqlite3 retail_sales.db < queries.sql   # or open in DB Browser for SQLite / run via Python
```

## Files
- `generate_data.py` — builds the SQLite database with synthetic but realistic data
- `retail_sales.db` — the database
- `queries.sql` — 10 commented analysis queries
- `app.py` — interactive Streamlit dashboard running the queries live
- `requirements.txt` — dependencies
