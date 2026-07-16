"""
Retail Sales Analysis — Streamlit Dashboard
Runs the SQL queries from queries.sql live against retail_sales.db
and shows the results as tables and charts.
"""
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Retail Sales Dashboard", page_icon="🛒", layout="wide")


@st.cache_resource
def get_connection():
    return sqlite3.connect("retail_sales.db", check_same_thread=False)


def run_query(sql):
    return pd.read_sql_query(sql, get_connection())


st.title("🛒 Retail Sales Analysis Dashboard")
st.caption("Live SQL queries (joins, aggregations, window functions) against a normalized retail sales database.")

conn = get_connection()
total_revenue = run_query(
    "SELECT ROUND(SUM(o.quantity * p.unit_price),2) AS rev FROM orders o JOIN products p ON o.product_id = p.product_id"
)["rev"][0]
total_orders = run_query("SELECT COUNT(*) AS n FROM orders")["n"][0]
total_customers = run_query("SELECT COUNT(*) AS n FROM customers")["n"][0]

k1, k2, k3 = st.columns(3)
k1.metric("Total Revenue", f"${total_revenue:,.2f}")
k2.metric("Total Orders", f"{total_orders:,}")
k3.metric("Customers", f"{total_customers:,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Revenue by Category & Region", "Monthly Trend", "Top Customers", "Churn Risk"]
)

# ---- Tab 1 ----
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by Category")
        cat_df = run_query(
            """
            SELECT p.category, ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue
            FROM orders o JOIN products p ON o.product_id = p.product_id
            GROUP BY p.category ORDER BY total_revenue DESC
            """
        )
        st.dataframe(cat_df, use_container_width=True, hide_index=True)
        fig, ax = plt.subplots()
        ax.bar(cat_df["category"], cat_df["total_revenue"], color="#1F3864")
        ax.set_ylabel("Revenue ($)")
        plt.xticks(rotation=20)
        st.pyplot(fig)

    with col2:
        st.subheader("Revenue by Region")
        region_df = run_query(
            """
            SELECT c.region, ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            GROUP BY c.region ORDER BY total_revenue DESC
            """
        )
        st.dataframe(region_df, use_container_width=True, hide_index=True)
        fig2, ax2 = plt.subplots()
        ax2.pie(region_df["total_revenue"], labels=region_df["region"], autopct="%1.0f%%")
        st.pyplot(fig2)

    st.subheader("Top 5 Products by Revenue")
    top_products = run_query(
        """
        SELECT p.product_name, p.category, ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue
        FROM orders o JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id ORDER BY total_revenue DESC LIMIT 5
        """
    )
    st.dataframe(top_products, use_container_width=True, hide_index=True)

# ---- Tab 2 ----
with tab2:
    st.subheader("Monthly Revenue Trend & Cumulative Revenue")
    monthly = run_query(
        """
        WITH monthly AS (
            SELECT strftime('%Y-%m', o.order_date) AS month,
                   SUM(o.quantity * p.unit_price) AS revenue
            FROM orders o JOIN products p ON o.product_id = p.product_id
            GROUP BY month
        )
        SELECT month, ROUND(revenue,2) AS revenue,
               ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct,
               ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative_revenue
        FROM monthly ORDER BY month
        """
    )
    st.dataframe(monthly, use_container_width=True, hide_index=True)

    fig3, ax3 = plt.subplots(figsize=(9, 4))
    ax3.plot(monthly["month"], monthly["revenue"], marker="o", label="Monthly Revenue")
    ax3.set_xticks(range(0, len(monthly), 2))
    ax3.set_xticklabels(monthly["month"][::2], rotation=45)
    ax3.set_ylabel("Revenue ($)")
    ax3.legend()
    st.pyplot(fig3)

# ---- Tab 3 ----
with tab3:
    st.subheader("Top 10 Customers by Lifetime Spend")
    top_customers = run_query(
        """
        SELECT c.customer_name, c.region,
               ROUND(SUM(o.quantity * p.unit_price), 2) AS lifetime_spend,
               COUNT(o.order_id) AS num_orders
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.customer_id ORDER BY lifetime_spend DESC LIMIT 10
        """
    )
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

    st.subheader("Top 3 Customers per Region (RANK)")
    ranked = run_query(
        """
        SELECT region, customer_name, lifetime_spend, rank_in_region
        FROM (
            SELECT region, customer_name, lifetime_spend,
                   RANK() OVER (PARTITION BY region ORDER BY lifetime_spend DESC) AS rank_in_region
            FROM (
                SELECT c.region, c.customer_name,
                       ROUND(SUM(o.quantity * p.unit_price), 2) AS lifetime_spend
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN products p ON o.product_id = p.product_id
                GROUP BY c.customer_id
            )
        )
        WHERE rank_in_region <= 3
        ORDER BY region, rank_in_region
        """
    )
    st.dataframe(ranked, use_container_width=True, hide_index=True)

# ---- Tab 4 ----
with tab4:
    st.subheader("Customers With No Orders in the Last 90 Days (Churn Risk)")
    at_risk = run_query(
        """
        SELECT c.customer_id, c.customer_name, MAX(o.order_date) AS last_order_date
        FROM customers c JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        HAVING last_order_date < (SELECT date(MAX(order_date), '-90 days') FROM orders)
        ORDER BY last_order_date
        """
    )
    st.dataframe(at_risk, use_container_width=True, hide_index=True)
    st.caption(f"{len(at_risk)} customers flagged as at risk of churn.")
