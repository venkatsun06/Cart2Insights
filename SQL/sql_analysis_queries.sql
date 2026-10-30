 Use cart2insights;
 
SELECT COUNT(*) AS total_orders
FROM orders;

# Find orders by status

SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;


# Calculate monthly revenue based on Order Month for the only delivered orders

WITH order_totals AS (
    SELECT order_id, SUM(price + freight_value) AS order_value
    FROM order_items
    GROUP BY order_id
)
SELECT
    DATE_FORMAT( o.order_purchase_timestamp, '%Y-%m') AS order_month,
    SUM(ot.order_value) AS merchandise_and_freight
FROM orders o
JOIN order_totals ot
    ON o.order_id = ot.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(
    o.order_purchase_timestamp, '%Y-%m'
)
ORDER BY order_month;


select * FROM order_items;

# To find the Top Selling based on Category_name

SELECT
        ct.product_category_name_english AS category_name,
	COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_sales
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY category_name
ORDER BY total_sales DESC
LIMIT 10;

#Examples of Join

SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id;
    
# Which Customers Spend More Than the Average Customer
    
WITH customer_spending AS
(
    SELECT
        c.customer_unique_id,
        ROUND(SUM(oi.price), 2) AS total_spent
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id)
SELECT
    customer_unique_id,
    total_spent
FROM customer_spending
WHERE total_spent >
(
    SELECT AVG(total_spent)
    FROM customer_spending
)
ORDER BY total_spent DESC;

# Find the Top Five Sellers by Revenue

WITH seller_revenue AS
(
    SELECT
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(*) AS total_items_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM sellers s
    JOIN order_items oi
        ON s.seller_id = oi.seller_id
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        s.seller_id,
        s.seller_city,
        s.seller_state
),
seller_ranking AS
(
    SELECT
        seller_id,
        seller_city,
        seller_state,
        total_items_sold,
        total_revenue,
        DENSE_RANK() OVER (
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM seller_revenue
)
SELECT *
FROM seller_ranking
WHERE revenue_rank <= 5
ORDER BY revenue_rank, seller_id;


# Each Customer's Spending Rank

WITH customer_spending AS
(
    SELECT
        c.customer_unique_id,

        COUNT(DISTINCT o.order_id) AS total_orders,

        ROUND(SUM(oi.price), 2) AS total_spent

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY c.customer_unique_id
)

SELECT
    customer_unique_id,
    total_orders,
    total_spent,

    RANK() OVER (
        ORDER BY total_spent DESC
    ) AS spending_rank

FROM customer_spending

ORDER BY spending_rank, customer_unique_id;

    
# What is the running monthly revenue

WITH monthly_revenue AS
(
    SELECT
        DATE_FORMAT(
            o.order_purchase_timestamp,
            '%Y-%m'
        ) AS order_month,

        ROUND(SUM(oi.price), 2) AS monthly_sales

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY
        DATE_FORMAT(
            o.order_purchase_timestamp,
            '%Y-%m'
        )
)

SELECT
    order_month,
    monthly_sales,

    ROUND(
        SUM(monthly_sales) OVER (
            ORDER BY order_month
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ), 2
    ) AS running_monthly_revenue

FROM monthly_revenue

ORDER BY order_month;



