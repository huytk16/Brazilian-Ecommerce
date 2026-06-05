-- Olist Brazilian E-Commerce core SQL analysis.
--
-- Expected SQLite tables loaded before running this script:
--   orders, items, payments, reviews, customers, sellers, products, translation
--
-- Grain rules:
--   1. df_master is order-level.
--   2. items, payments, and reviews are aggregated before joining to df_master.
--   3. category/seller analyses use item_detail because one order may contain multiple items.

DROP VIEW IF EXISTS order_item_agg;
CREATE VIEW order_item_agg AS
SELECT
    order_id,
    COUNT(*) AS item_count,
    COUNT(DISTINCT product_id) AS product_count,
    COUNT(DISTINCT seller_id) AS seller_count,
    SUM(price) AS item_price,
    SUM(freight_value) AS freight_value,
    SUM(price + freight_value) AS item_gmv
FROM items
GROUP BY order_id;

DROP VIEW IF EXISTS payment_agg;
CREATE VIEW payment_agg AS
SELECT
    order_id,
    COUNT(*) AS payment_count,
    SUM(payment_value) AS payment_value,
    MAX(payment_installments) AS max_installments,
    MIN(payment_type) AS primary_payment_type
FROM payments
GROUP BY order_id;

DROP VIEW IF EXISTS review_agg;
CREATE VIEW review_agg AS
SELECT
    order_id,
    COUNT(DISTINCT review_id) AS review_count,
    AVG(review_score) AS review_score
FROM reviews
GROUP BY order_id;

DROP VIEW IF EXISTS product_dim;
CREATE VIEW product_dim AS
SELECT
    p.product_id,
    COALESCE(t.product_category_name_english, 'unknown') AS product_category_name_english,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM products p
LEFT JOIN translation t
    ON p.product_category_name = t.product_category_name;

DROP VIEW IF EXISTS df_master;
CREATE VIEW df_master AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_status,
    o.order_purchase_timestamp,
    SUBSTR(o.order_purchase_timestamp, 1, 7) AS purchase_month,
    CAST(SUBSTR(o.order_purchase_timestamp, 1, 4) AS INTEGER) AS purchase_year,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.product_count, 0) AS product_count,
    COALESCE(i.seller_count, 0) AS seller_count,
    COALESCE(i.item_price, 0) AS item_price,
    COALESCE(i.freight_value, 0) AS freight_value,
    COALESCE(i.item_gmv, 0) AS item_gmv,
    COALESCE(p.payment_count, 0) AS payment_count,
    COALESCE(p.payment_value, 0) AS payment_value,
    p.max_installments,
    p.primary_payment_type,
    r.review_count,
    r.review_score,
    CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END AS delivered_flag,
    CASE
        WHEN o.order_status <> 'delivered' THEN NULL
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1.0
        ELSE 0.0
    END AS late_flag,
    CASE
        WHEN o.order_status <> 'delivered' THEN NULL
        ELSE julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)
    END AS delivery_days
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
LEFT JOIN order_item_agg i
    ON o.order_id = i.order_id
LEFT JOIN payment_agg p
    ON o.order_id = p.order_id
LEFT JOIN review_agg r
    ON o.order_id = r.order_id;

DROP VIEW IF EXISTS item_detail;
CREATE VIEW item_detail AS
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    i.price,
    i.freight_value,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    SUBSTR(o.order_purchase_timestamp, 1, 7) AS purchase_month,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    c.customer_state,
    s.seller_state,
    pd.product_category_name_english,
    r.review_score,
    CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END AS delivered_flag,
    CASE
        WHEN o.order_status <> 'delivered' THEN NULL
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1.0
        ELSE 0.0
    END AS late_flag
FROM items i
LEFT JOIN orders o
    ON i.order_id = o.order_id
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
LEFT JOIN sellers s
    ON i.seller_id = s.seller_id
LEFT JOIN product_dim pd
    ON i.product_id = pd.product_id
LEFT JOIN review_agg r
    ON i.order_id = r.order_id;

DROP VIEW IF EXISTS yearly_kpis;
CREATE VIEW yearly_kpis AS
SELECT
    purchase_year AS year,
    COUNT(DISTINCT order_id) AS delivered_orders,
    SUM(payment_value) AS payment_revenue,
    SUM(item_price) AS item_price_revenue,
    SUM(freight_value) AS freight_revenue,
    SUM(payment_value) / COUNT(DISTINCT order_id) AS aov_payment,
    AVG(1.0 - late_flag) AS on_time_rate,
    AVG(late_flag) AS late_rate,
    AVG(review_score) AS avg_review_score,
    AVG(delivery_days) AS avg_delivery_days
FROM df_master
WHERE delivered_flag = 1
  AND purchase_year IN (2017, 2018)
GROUP BY purchase_year;

DROP VIEW IF EXISTS monthly_kpis;
CREATE VIEW monthly_kpis AS
SELECT
    purchase_month,
    COUNT(DISTINCT order_id) AS delivered_orders,
    SUM(payment_value) AS payment_revenue,
    SUM(item_price) AS item_price_revenue,
    AVG(late_flag) AS late_rate,
    AVG(review_score) AS avg_review_score
FROM df_master
WHERE delivered_flag = 1
GROUP BY purchase_month;

DROP VIEW IF EXISTS category_performance;
CREATE VIEW category_performance AS
SELECT
    product_category_name_english,
    SUM(price) AS item_price_revenue,
    SUM(freight_value) AS freight_value,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(*) AS items,
    AVG(review_score) AS avg_review_score,
    AVG(late_flag) AS late_rate,
    AVG(freight_value) AS avg_freight_per_item,
    SUM(price) / COUNT(DISTINCT order_id) AS aov_item_price,
    SUM(price) * COALESCE(AVG(review_score), 0) AS weighted_objective
FROM item_detail
WHERE delivered_flag = 1
GROUP BY product_category_name_english;

DROP VIEW IF EXISTS customer_state_logistics;
CREATE VIEW customer_state_logistics AS
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS orders,
    SUM(payment_value) AS payment_revenue,
    AVG(delivery_days) AS avg_delivery_days,
    AVG(late_flag) AS late_rate,
    AVG(freight_value) AS avg_freight,
    AVG(review_score) AS avg_review_score
FROM df_master
WHERE delivered_flag = 1
GROUP BY customer_state
HAVING COUNT(DISTINCT order_id) >= 30;

DROP VIEW IF EXISTS seller_performance;
CREATE VIEW seller_performance AS
SELECT
    seller_id,
    seller_state,
    COUNT(DISTINCT order_id) AS orders,
    SUM(price) AS item_price_revenue,
    AVG(review_score) AS avg_review_score,
    AVG(late_flag) AS late_rate,
    AVG(freight_value) AS avg_freight_per_item
FROM item_detail
WHERE delivered_flag = 1
GROUP BY seller_id, seller_state
HAVING COUNT(DISTINCT order_id) >= 30;
