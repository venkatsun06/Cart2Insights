
# queries.py

OVERVIEW = {
    "revenue": """
        SELECT COALESCE(SUM(price), 0)
        FROM order_items
        WHERE order_id IN (
            SELECT order_id FROM orders
            WHERE order_status NOT IN ('canceled', 'unavailable')
        )
    """,
    "orders": """
        SELECT COUNT(DISTINCT order_id)
        FROM orders
    """,
    "customers": """
        SELECT COUNT(DISTINCT customer_id)
        FROM customers
    """,
    "sellers": """
        SELECT COUNT(DISTINCT seller_id)
        FROM sellers
    """,
    "avg_order_value": """
        SELECT COALESCE(AVG(order_total), 0)
        FROM (
            SELECT o.order_id, SUM(oi.price) AS order_total
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status NOT IN ('canceled', 'unavailable')
            GROUP BY o.order_id
        ) totals
    """,
    "avg_review": """
        SELECT COALESCE(AVG(review_score), 0)
        FROM reviews
    """
}

MONTHLY_REVENUE = """
    SELECT DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
           SUM(oi.price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY month
    ORDER BY month
"""

CATEGORY_REVENUE = """
    SELECT COALESCE(
               ct.product_category_name_english,
               p.product_category_name,
               'Unknown'
           ) AS category,
           SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY category
    ORDER BY revenue DESC
    LIMIT 10
"""

TOP_PRODUCTS = """
    SELECT oi.product_id, SUM(oi.price) AS revenue,
           COUNT(*) AS items_sold
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY oi.product_id
    ORDER BY items_sold DESC
    LIMIT 10
"""

STATE_REVENUE = """
    SELECT c.customer_state AS state, SUM(oi.price) AS revenue
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_state
    ORDER BY revenue DESC
"""

TOP_CUSTOMERS = """
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id) AS orders_count,
           SUM(oi.price) AS spending
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
    ORDER BY spending DESC
    LIMIT 10
"""

REPEAT_CUSTOMERS = """
    SELECT COUNT(*) FROM (
        SELECT c.customer_unique_id
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
        HAVING COUNT(DISTINCT o.order_id) > 1
    ) repeat_buyers
"""

TOP_SELLERS = """
    SELECT oi.seller_id, SUM(oi.price) AS revenue,
           COUNT(DISTINCT oi.order_id) AS orders_count
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY oi.seller_id
    ORDER BY revenue DESC
    LIMIT 10
"""

DELIVERY_METRICS = """
    SELECT
        AVG(DATEDIFF(
            order_delivered_customer_date,
            order_purchase_timestamp
        )) AS avg_delivery_days,
        SUM(
            CASE WHEN order_delivered_customer_date >
                      order_estimated_delivery_date
                 THEN 1 ELSE 0 END
        ) AS delayed_orders,
        COUNT(order_delivered_customer_date) AS delivered_orders
    FROM orders
    WHERE order_delivered_customer_date IS NOT NULL
"""

DELIVERY_BY_STATE = """
    SELECT c.customer_state AS state,
           AVG(DATEDIFF(
               o.order_delivered_customer_date,
               o.order_purchase_timestamp
           )) AS avg_delivery_days
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_delivered_customer_date IS NOT NULL
    GROUP BY c.customer_state
    ORDER BY avg_delivery_days DESC
"""

REVIEW_DISTRIBUTION = """
    SELECT review_score, COUNT(*) AS review_count
    FROM reviews
    WHERE review_score IS NOT NULL
    GROUP BY review_score
    ORDER BY review_score
"""

CATEGORY_REVIEWS = """
    SELECT COALESCE(
               ct.product_category_name_english,
               p.product_category_name,
               'Unknown'
           ) AS category,
           AVG(r.review_score) AS avg_review,
           COUNT(*) AS review_count
    FROM reviews r
    JOIN order_items oi ON r.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name
    WHERE r.review_score IS NOT NULL
    GROUP BY category
    ORDER BY avg_review DESC
    LIMIT 10
"""

DELAY_REVIEW = """
    SELECT
        CASE
            WHEN o.order_delivered_customer_date >
                 o.order_estimated_delivery_date
            THEN 'Delayed'
            ELSE 'On time or early'
        END AS delivery_status,
        AVG(r.review_score) AS avg_review
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_delivered_customer_date IS NOT NULL
    GROUP BY delivery_status
"""
