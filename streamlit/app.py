
# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from database import engine
import queries as q
from utils import format_number, format_currency

st.set_page_config(
    page_title="Cart2Insights",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Cart2Insights")
st.subheader("E-Commerce Performance Dashboard")
st.caption("Explore sales, customers, products, delivery and reviews.")

# ---------- Helper functions ----------

@st.cache_data(ttl=300)
def load_data(sql):
    """Run a SELECT query and return the result as a DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql(text(sql), connection)


def get_value(sql):
    """Return the first value from a one-cell query."""
    df = load_data(sql)
    return df.iloc[0, 0] if not df.empty else 0


def show_kpi(label, value):
    st.metric(label, value)


# ---------- Load overview values ----------

try:
    revenue = get_value(q.OVERVIEW["revenue"])
    order_count = get_value(q.OVERVIEW["orders"])
    customer_count = get_value(q.OVERVIEW["customers"])
    seller_count = get_value(q.OVERVIEW["sellers"])
    avg_order_value = get_value(q.OVERVIEW["avg_order_value"])
    avg_review = get_value(q.OVERVIEW["avg_review"])

except Exception as error:
    st.error(
        "Could not load data from MySQL. "
        "Check your database connection and table names."
    )
    st.exception(error)
    st.stop()


# ---------- Six dashboard sections ----------

overview_tab, sales_tab, customer_tab, seller_tab, delivery_tab, experience_tab = st.tabs([
    "Business Overview",
    "Sales Analysis",
    "Customer Analysis",
    "Seller & Product Analysis",
    "Delivery Analysis",
    "Customer Experience"
])


# 1. BUSINESS OVERVIEW
with overview_tab:
    st.header("Business Overview")
    st.write("A high-level summary of business performance.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", format_currency(float(revenue or 0)))
    c2.metric("Total Orders", format_number(int(order_count or 0)))
    c3.metric("Total Customers", format_number(int(customer_count or 0)))

    c4, c5, c6 = st.columns(3)
    c4.metric("Total Sellers", format_number(int(seller_count or 0)))
    c5.metric("Average Order Value", format_currency(float(avg_order_value or 0)))
    c6.metric("Average Review Score", f"{float(avg_review or 0):.2f} / 5")

    st.info(
        "Revenue is calculated from item prices and excludes freight charges."
    )


# 2. SALES ANALYSIS
with sales_tab:
    st.header("Sales Analysis")

    monthly = load_data(q.MONTHLY_REVENUE)
    categories = load_data(q.CATEGORY_REVENUE)
    products = load_data(q.TOP_PRODUCTS)
    locations = load_data(q.STATE_REVENUE)

    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue")
        if not monthly.empty:
            fig = px.line(
                monthly, x="month", y="revenue",
                markers=True, title="Revenue by Month"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly revenue data available.")

    with right:
        st.subheader("Revenue by Product Category")
        if not categories.empty:
            fig = px.bar(
                categories.sort_values("revenue"),
                x="revenue", y="category",
                orientation="h", title="Top Categories by Revenue"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available.")

    left, right = st.columns(2)

    with left:
        st.subheader("Top-Selling Products")
        if not products.empty:
            st.dataframe(products, use_container_width=True, hide_index=True)
        else:
            st.info("No product data available.")

    with right:
        st.subheader("Revenue by Customer State")
        if not locations.empty:
            fig = px.bar(
                locations, x="state", y="revenue",
                title="Revenue by State"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No location data available.")


# 3. CUSTOMER ANALYSIS
with customer_tab:
    st.header("Customer Analysis")

    repeat_count = get_value(q.REPEAT_CUSTOMERS)
    top_customers = load_data(q.TOP_CUSTOMERS)

    c1, c2 = st.columns(2)
    c1.metric("Total Customers", format_number(int(customer_count or 0)))
    c2.metric("Repeat Customers", format_number(int(repeat_count or 0)))

    st.subheader("Top Customers by Spending")
    if not top_customers.empty:
        top_customers["spending"] = top_customers["spending"].round(2)
        st.dataframe(
            top_customers,
            use_container_width=True,
            hide_index=True
        )
        fig = px.bar(
            top_customers.sort_values("spending"),
            x="spending",
            y="customer_unique_id",
            orientation="h",
            title="Top 10 Customers by Spending"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer spending data available.")

    st.caption(
        "Repeat customers are counted by unique customer identity, "
        "not by individual customer_id."
    )


# 4. SELLER & PRODUCT ANALYSIS
with seller_tab:
    st.header("Seller & Product Analysis")

    sellers = load_data(q.TOP_SELLERS)
    categories = load_data(q.CATEGORY_REVENUE)

    left, right = st.columns(2)

    with left:
        st.subheader("Top Sellers by Revenue")
        if not sellers.empty:
            st.dataframe(sellers, use_container_width=True, hide_index=True)
            fig = px.bar(
                sellers.sort_values("revenue"),
                x="revenue", y="seller_id",
                orientation="h", title="Top 10 Sellers"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No seller data available.")

    with right:
        st.subheader("Category Performance")
        if not categories.empty:
            fig = px.bar(
                categories.sort_values("revenue"),
                x="revenue", y="category",
                orientation="h", title="Revenue by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available.")


# 5. DELIVERY ANALYSIS
with delivery_tab:
    st.header("Delivery Analysis")

    delivery = load_data(q.DELIVERY_METRICS)
    state_delivery = load_data(q.DELIVERY_BY_STATE)

    if not delivery.empty:
        row = delivery.iloc[0]
        avg_days = row["avg_delivery_days"]
        delayed = int(row["delayed_orders"] or 0)
        delivered = int(row["delivered_orders"] or 0)

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Average Delivery Time",
            f"{float(avg_days):.1f} days" if pd.notna(avg_days) else "N/A"
        )
        c2.metric("Delayed Orders", format_number(delayed))
        c3.metric("Delivered Orders", format_number(delivered))

        delay_rate = (delayed / delivered * 100) if delivered else 0
        st.metric("Delay Rate", f"{delay_rate:.2f}%")

    st.subheader("Average Delivery Time by State")
    if not state_delivery.empty:
        fig = px.bar(
            state_delivery.sort_values("avg_delivery_days"),
            x="avg_delivery_days",
            y="state",
            orientation="h",
            title="Average Delivery Days by State"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivery data available.")


# 6. CUSTOMER EXPERIENCE
with experience_tab:
    st.header("Customer Experience")

    reviews = load_data(q.REVIEW_DISTRIBUTION)
    category_reviews = load_data(q.CATEGORY_REVIEWS)
    delay_reviews = load_data(q.DELAY_REVIEW)

    left, right = st.columns(2)

    with left:
        st.subheader("Review Score Distribution")
        if not reviews.empty:
            fig = px.bar(
                reviews,
                x="review_score",
                y="review_count",
                title="Number of Reviews by Score"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No review data available.")

    with right:
        st.subheader("Average Review by Delivery Status")
        if not delay_reviews.empty:
            fig = px.bar(
                delay_reviews,
                x="delivery_status",
                y="avg_review",
                title="Delivery Timing vs Review Score"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No delivery/review data available.")

    st.subheader("Customer Reviews by Product Category")
    if not category_reviews.empty:
        st.dataframe(
            category_reviews,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No category review data available.")

st.divider()
st.caption("Cart2Insights | E-Commerce Analytics Project")
