-- ============================================================
-- Olist DWH — Sample Analytical Queries (Reporting Layer)
-- ============================================================


-- ----------------------------------------------------------------
-- Q1: Sales Trend Over Time (Monthly Revenue)
-- Business Question: How are sales trending over time?
-- ----------------------------------------------------------------
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id)        AS total_orders,
    COUNT(f.order_item_sk)            AS total_items_sold,
    ROUND(SUM(f.total_item_value), 2) AS total_revenue,
    ROUND(AVG(f.price), 2)            AS avg_item_price
FROM dwh.fact_order_items f
JOIN dwh.dim_date d ON f.purchase_date_sk = d.date_sk
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- ----------------------------------------------------------------
-- Q2: Most Valuable Customers (Customer Lifetime Value)
-- Business Question: Who are the most valuable customers?
-- ----------------------------------------------------------------
SELECT
    c.customer_unique_id,
    g.city,
    g.state,
    COUNT(DISTINCT f.order_id)        AS total_orders,
    ROUND(SUM(f.total_item_value), 2) AS lifetime_value,
    ROUND(AVG(f.price), 2)            AS avg_item_price,
    ROUND(AVG(f.freight_value), 2)    AS avg_freight_paid
FROM dwh.fact_order_items f
JOIN dwh.dim_customers c    ON f.customer_sk = c.customer_sk
JOIN dwh.dim_geolocation g  ON c.geolocation_sk = g.geolocation_sk
GROUP BY c.customer_unique_id, g.city, g.state
ORDER BY lifetime_value DESC
LIMIT 20;


-- ----------------------------------------------------------------
-- Q3: Delivery Performance by State
-- Business Question: What affects delivery performance?
-- ----------------------------------------------------------------
SELECT
    g.state,
    COUNT(*)                                                          AS total_orders,
    ROUND(AVG(fp.customer_delivery_days), 2)                          AS avg_delivery_days,
    ROUND(AVG(fp.approval_hours), 2)                                  AS avg_approval_hours,
    SUM(CASE WHEN fp.is_late THEN 1 ELSE 0 END)                       AS late_orders,
    ROUND(
        100.0 * SUM(CASE WHEN fp.is_late THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                                 AS late_rate_pct
FROM dwh.fact_delivery_performance fp
JOIN dwh.dim_customers c    ON fp.customer_sk = c.customer_sk
JOIN dwh.dim_geolocation g  ON c.geolocation_sk = g.geolocation_sk
WHERE fp.customer_delivery_days IS NOT NULL
GROUP BY g.state
ORDER BY late_rate_pct DESC;


-- ----------------------------------------------------------------
-- Q4: Top Revenue-Driving Product Categories
-- Business Question: Which products/categories drive revenue?
-- ----------------------------------------------------------------
SELECT
    p.product_category_name_english,
    COUNT(f.order_item_sk)            AS items_sold,
    ROUND(SUM(f.price), 2)            AS total_revenue,
    ROUND(SUM(f.freight_value), 2)    AS total_freight_cost,
    ROUND(AVG(f.price), 2)            AS avg_item_price,
    ROUND(AVG(f.freight_value), 2)    AS avg_freight
FROM dwh.fact_order_items f
JOIN dwh.dim_products p ON f.product_sk = p.product_sk
WHERE p.product_category_name_english <> 'unknown'
GROUP BY p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 15;


-- ----------------------------------------------------------------
-- Q5: Customer Satisfaction by Product Category
-- Business Question: Which categories receive the best/worst reviews?
-- ----------------------------------------------------------------
SELECT
    p.product_category_name_english,
    COUNT(r.review_sk)                                              AS review_count,
    ROUND(AVG(r.review_score), 2)                                   AS avg_score,
    SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END)             AS five_star,
    SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END)            AS low_score,
    SUM(CASE WHEN r.has_comment THEN 1 ELSE 0 END)                  AS reviews_with_comment
FROM dwh.fact_reviews r
JOIN dwh.fact_order_items f  ON r.order_id = f.order_id
JOIN dwh.dim_products p      ON f.product_sk = p.product_sk
WHERE p.product_category_name_english <> 'unknown'
GROUP BY p.product_category_name_english
ORDER BY avg_score ASC
LIMIT 15;


-- ----------------------------------------------------------------
-- Q6: Payment Method Distribution
-- Business Question: How do customers prefer to pay?
-- ----------------------------------------------------------------
SELECT
    pt.payment_type,
    COUNT(*)                             AS payment_count,
    ROUND(SUM(fp.payment_value), 2)      AS total_value,
    ROUND(AVG(fp.payment_value), 2)      AS avg_payment,
    ROUND(AVG(fp.payment_installments), 2) AS avg_installments
FROM dwh.fact_payments fp
JOIN dwh.dim_payment_type pt ON fp.payment_type_sk = pt.payment_type_sk
GROUP BY pt.payment_type
ORDER BY total_value DESC;


-- ----------------------------------------------------------------
-- Q7: Seller Lead Conversion by Acquisition Channel
-- Business Question: Which marketing channels convert best?
-- ----------------------------------------------------------------
SELECT
    lo.origin,
    COUNT(*)                                                          AS total_leads,
    SUM(CASE WHEN sl.is_closed THEN 1 ELSE 0 END)                    AS converted,
    ROUND(
        100.0 * SUM(CASE WHEN sl.is_closed THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                                 AS conversion_rate_pct,
    ROUND(AVG(sl.days_to_close) FILTER (WHERE sl.is_closed), 2)      AS avg_days_to_close,
    ROUND(AVG(sl.declared_monthly_revenue) FILTER (WHERE sl.is_closed), 2) AS avg_declared_revenue
FROM dwh.fact_seller_leads sl
JOIN dwh.dim_lead_origin lo ON sl.lead_origin_sk = lo.lead_origin_sk
GROUP BY lo.origin
ORDER BY total_leads DESC;


-- ----------------------------------------------------------------
-- Q8: Quarterly Revenue Growth Rate
-- Business Question: Is the business growing quarter over quarter?
-- ----------------------------------------------------------------
WITH quarterly AS (
    SELECT
        d.year,
        d.quarter,
        ROUND(SUM(f.total_item_value), 2) AS revenue
    FROM dwh.fact_order_items f
    JOIN dwh.dim_date d ON f.purchase_date_sk = d.date_sk
    GROUP BY d.year, d.quarter
)
SELECT
    year,
    quarter,
    revenue,
    LAG(revenue) OVER (ORDER BY year, quarter)  AS prev_quarter_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, quarter))
              / NULLIF(LAG(revenue) OVER (ORDER BY year, quarter), 0),
        2
    ) AS growth_rate_pct
FROM quarterly
ORDER BY year, quarter;


-- ----------------------------------------------------------------
-- Q9: Late Delivery Impact on Review Score
-- Business Question: Do late deliveries cause lower review scores?
-- ----------------------------------------------------------------
SELECT
    dp.is_late,
    COUNT(r.review_sk)            AS review_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star_count,
    SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) AS low_score_count
FROM dwh.fact_reviews r
JOIN dwh.fact_delivery_performance dp ON r.order_id = dp.order_id
WHERE dp.is_late IS NOT NULL
GROUP BY dp.is_late
ORDER BY dp.is_late;
