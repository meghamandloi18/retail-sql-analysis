-- ============================================================
-- Retail Sales Analysis — SQL queries
-- Database: retail_sales.db (customers, products, orders)
-- ============================================================

-- 1. Total revenue by product category
SELECT
    p.category,
    ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue,
    SUM(o.quantity) AS units_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 2. Top 5 best-selling products by revenue
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue,
    SUM(o.quantity) AS units_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 5;

-- 3. Revenue by region
SELECT
    c.region,
    ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue,
    COUNT(DISTINCT o.customer_id) AS num_customers
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.region
ORDER BY total_revenue DESC;

-- 4. Monthly revenue trend
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY month
ORDER BY month;

-- 5. Month-over-month revenue growth (%) using a window function
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(o.quantity * p.unit_price) AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / LAG(revenue) OVER (ORDER BY month), 1
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- 6. Top 10 customers by lifetime spend
SELECT
    c.customer_name,
    c.region,
    ROUND(SUM(o.quantity * p.unit_price), 2) AS lifetime_spend,
    COUNT(o.order_id) AS num_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id
ORDER BY lifetime_spend DESC
LIMIT 10;

-- 7. Top 3 customers by spend within each region, using RANK()
SELECT region, customer_name, lifetime_spend, rank_in_region
FROM (
    SELECT
        region,
        customer_name,
        lifetime_spend,
        RANK() OVER (PARTITION BY region ORDER BY lifetime_spend DESC) AS rank_in_region
    FROM (
        SELECT
            c.region,
            c.customer_name,
            ROUND(SUM(o.quantity * p.unit_price), 2) AS lifetime_spend
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.customer_id
    )
)
WHERE rank_in_region <= 3
ORDER BY region, rank_in_region;

-- 8. Average order value (AOV) by category
SELECT
    p.category,
    ROUND(AVG(o.quantity * p.unit_price), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_order_value DESC;

-- 9. Customers who haven't ordered in the last 90 days of the dataset (churn risk)
SELECT
    c.customer_id,
    c.customer_name,
    MAX(o.order_date) AS last_order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING last_order_date < (
    SELECT date(MAX(order_date), '-90 days') FROM orders
)
ORDER BY last_order_date;

-- 10. Running total of revenue over time (cumulative sum window function)
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        SUM(o.quantity * p.unit_price) AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
FROM monthly
ORDER BY month;
