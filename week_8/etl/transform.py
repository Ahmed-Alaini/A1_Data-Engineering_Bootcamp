import pandas as pd


def build_dim_date(engine):
    query = """
        SELECT DISTINCT
            TO_CHAR(d::DATE, 'YYYYMMDD')::INTEGER AS date_sk,
            d::DATE AS full_date,
            EXTRACT(YEAR FROM d)::INTEGER AS year,
            EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
            EXTRACT(MONTH FROM d)::INTEGER AS month,
            TRIM(TO_CHAR(d::DATE, 'Month')) AS month_name,
            EXTRACT(DAY FROM d)::INTEGER AS day,
            EXTRACT(ISODOW FROM d)::INTEGER AS day_of_week,
            TRIM(TO_CHAR(d::DATE, 'Day')) AS day_name,
            CASE 
                WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN TRUE 
                ELSE FALSE 
            END AS is_weekend
        FROM (
            SELECT order_purchase_timestamp::TIMESTAMP::DATE AS d
            FROM staging.orders
            WHERE order_purchase_timestamp IS NOT NULL

            UNION

            SELECT order_approved_at::TIMESTAMP::DATE
            FROM staging.orders
            WHERE order_approved_at IS NOT NULL

            UNION

            SELECT order_delivered_carrier_date::TIMESTAMP::DATE
            FROM staging.orders
            WHERE order_delivered_carrier_date IS NOT NULL

            UNION

            SELECT order_delivered_customer_date::TIMESTAMP::DATE
            FROM staging.orders
            WHERE order_delivered_customer_date IS NOT NULL

            UNION

            SELECT order_estimated_delivery_date::TIMESTAMP::DATE
            FROM staging.orders
            WHERE order_estimated_delivery_date IS NOT NULL

            UNION

            SELECT review_creation_date::TIMESTAMP::DATE
            FROM staging.order_reviews
            WHERE review_creation_date IS NOT NULL

            UNION

            SELECT review_answer_timestamp::TIMESTAMP::DATE
            FROM staging.order_reviews
            WHERE review_answer_timestamp IS NOT NULL

            UNION

            SELECT first_contact_date::TIMESTAMP::DATE
            FROM staging.leads_qualified
            WHERE first_contact_date IS NOT NULL

            UNION

            SELECT won_date::TIMESTAMP::DATE
            FROM staging.leads_closed
            WHERE won_date IS NOT NULL
            
            ) dates
        WHERE d IS NOT NULL
        ORDER BY full_date;
    """
    return pd.read_sql(query, engine)


def build_dim_geolocation(engine):
    query = """
        SELECT
            geolocation_zip_code_prefix::BIGINT AS zip_code,
            AVG(geolocation_lat) AS latitude,
            AVG(geolocation_lng) AS longitude,
            MIN(geolocation_city) AS city,
            MIN(geolocation_state) AS state
        FROM staging.geolocation
        WHERE geolocation_zip_code_prefix IS NOT NULL
        GROUP BY geolocation_zip_code_prefix;
    """
    return pd.read_sql(query, engine)


def build_dim_products(engine):
    query = """
        SELECT DISTINCT
            p.product_id,
            COALESCE(p.product_category_name, 'unknown') AS product_category_name,
            COALESCE(t.product_category_name_english, 'unknown') AS product_category_name_english,
            p.product_name_lenght::INTEGER AS product_name_length,
            p.product_description_lenght::INTEGER AS product_description_length,
            p.product_photos_qty::INTEGER,
            p.product_weight_g::NUMERIC,
            p.product_length_cm::NUMERIC,
            p.product_height_cm::NUMERIC,
            p.product_width_cm::NUMERIC
        FROM staging.products p
        LEFT JOIN staging.product_category_name_translation t
            ON p.product_category_name = t.product_category_name;
    """
    return pd.read_sql(query, engine)


def build_dim_order_status(engine):
    query = """
        SELECT DISTINCT order_status
        FROM staging.orders
        WHERE order_status IS NOT NULL
        ORDER BY order_status;
    """
    return pd.read_sql(query, engine)


def build_dim_payment_type(engine):
    query = """
        SELECT DISTINCT payment_type
        FROM staging.order_payments
        WHERE payment_type IS NOT NULL
        ORDER BY payment_type;
    """
    return pd.read_sql(query, engine)


def build_dim_customers(engine):
    query = """
        SELECT DISTINCT
            c.customer_id,
            c.customer_unique_id,
            g.geolocation_sk
        FROM staging.customers c
        LEFT JOIN dwh.dim_geolocation g
            ON c.customer_zip_code_prefix::BIGINT = g.zip_code;
    """
    return pd.read_sql(query, engine)


def build_dim_sellers(engine):
    query = """
        SELECT DISTINCT
            s.seller_id,
            g.geolocation_sk
        FROM staging.sellers s
        LEFT JOIN dwh.dim_geolocation g
            ON s.seller_zip_code_prefix::BIGINT = g.zip_code;
    """
    return pd.read_sql(query, engine)

def build_dim_lead_origin(engine):
    query = """
        SELECT DISTINCT
            origin,
            landing_page_id
        FROM staging.leads_qualified;
    """
    return pd.read_sql(query, engine)

def build_dim_lead_profile(engine):
    query = """
        SELECT DISTINCT
            lead_type,
            lead_behaviour_profile,
            business_type,
            average_stock,

            CASE
                WHEN has_company IS NULL THEN NULL
                WHEN has_company::NUMERIC = 1 THEN TRUE
                WHEN has_company::NUMERIC = 0 THEN FALSE
                ELSE NULL
            END AS has_company,

            CASE
                WHEN has_gtin IS NULL THEN NULL
                WHEN has_gtin::NUMERIC = 1 THEN TRUE
                WHEN has_gtin::NUMERIC = 0 THEN FALSE
                ELSE NULL
            END AS has_gtin

        FROM staging.leads_closed;
    """
    return pd.read_sql(query, engine)


def build_dim_business_segment(engine):
    query = """
        SELECT DISTINCT
            business_segment
        FROM staging.leads_closed
        WHERE business_segment IS NOT NULL;
    """
    return pd.read_sql(query, engine)


    # ********build Fact Tables ************************
    
def build_fact_order_items(engine):
    query = """
        SELECT
            oi.order_id,
            oi.order_item_id::INTEGER AS order_item_id,
            dc.customer_sk,
            dp.product_sk,
            ds.seller_sk,
            dos.order_status_sk,
            TO_CHAR(o.order_purchase_timestamp::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER AS purchase_date_sk,
            oi.price::NUMERIC AS price,
            oi.freight_value::NUMERIC AS freight_value,
            (oi.price::NUMERIC + oi.freight_value::NUMERIC) AS total_item_value
        FROM staging.order_items oi
        JOIN staging.orders o
            ON oi.order_id = o.order_id
        LEFT JOIN dwh.dim_customers dc
            ON o.customer_id = dc.customer_id
        LEFT JOIN dwh.dim_products dp
            ON oi.product_id = dp.product_id
        LEFT JOIN dwh.dim_sellers ds
            ON oi.seller_id = ds.seller_id
        LEFT JOIN dwh.dim_order_status dos
            ON o.order_status = dos.order_status;
    """
    return pd.read_sql(query, engine)


def build_fact_payments(engine):
    query = """
        SELECT
            op.order_id,
            op.payment_sequential::INTEGER AS payment_sequential,
            dc.customer_sk,
            dpt.payment_type_sk,
            TO_CHAR(o.order_purchase_timestamp::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER AS purchase_date_sk,
            op.payment_installments::INTEGER AS payment_installments,
            op.payment_value::NUMERIC AS payment_value
        FROM staging.order_payments op
        JOIN staging.orders o
            ON op.order_id = o.order_id
        LEFT JOIN dwh.dim_customers dc
            ON o.customer_id = dc.customer_id
        LEFT JOIN dwh.dim_payment_type dpt
            ON op.payment_type = dpt.payment_type;
    """
    return pd.read_sql(query, engine)


def build_fact_delivery_performance(engine):
    query = """
        SELECT
            o.order_id,
            dc.customer_sk,
            dos.order_status_sk,

            CASE 
                WHEN o.order_purchase_timestamp IS NOT NULL
                THEN TO_CHAR(o.order_purchase_timestamp::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS purchase_date_sk,

            CASE 
                WHEN o.order_approved_at IS NOT NULL
                THEN TO_CHAR(o.order_approved_at::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS approved_date_sk,

            CASE 
                WHEN o.order_delivered_carrier_date IS NOT NULL
                THEN TO_CHAR(o.order_delivered_carrier_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS delivered_carrier_date_sk,

            CASE 
                WHEN o.order_delivered_customer_date IS NOT NULL
                THEN TO_CHAR(o.order_delivered_customer_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS delivered_customer_date_sk,

            CASE 
                WHEN o.order_estimated_delivery_date IS NOT NULL
                THEN TO_CHAR(o.order_estimated_delivery_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS estimated_delivery_date_sk,

            EXTRACT(EPOCH FROM (
                o.order_approved_at::TIMESTAMP - o.order_purchase_timestamp::TIMESTAMP
            )) / 3600 AS approval_hours,

            EXTRACT(EPOCH FROM (
                o.order_delivered_carrier_date::TIMESTAMP - o.order_approved_at::TIMESTAMP
            )) / 86400 AS carrier_delivery_days,

            EXTRACT(EPOCH FROM (
                o.order_delivered_customer_date::TIMESTAMP - o.order_purchase_timestamp::TIMESTAMP
            )) / 86400 AS customer_delivery_days,

            EXTRACT(EPOCH FROM (
                o.order_delivered_customer_date::TIMESTAMP - o.order_estimated_delivery_date::TIMESTAMP
            )) / 86400 AS estimated_vs_actual_days,

            CASE
                WHEN o.order_delivered_customer_date IS NULL THEN NULL
                WHEN o.order_estimated_delivery_date IS NULL THEN NULL
                WHEN o.order_delivered_customer_date::TIMESTAMP > o.order_estimated_delivery_date::TIMESTAMP THEN TRUE
                ELSE FALSE
            END AS is_late

        FROM staging.orders o
        LEFT JOIN dwh.dim_customers dc
            ON o.customer_id = dc.customer_id
        LEFT JOIN dwh.dim_order_status dos
            ON o.order_status = dos.order_status;
    """
    return pd.read_sql(query, engine)


def build_fact_reviews(engine):
    query = """
        SELECT
            r.review_id,
            r.order_id,
            dc.customer_sk,

            CASE
                WHEN r.review_creation_date IS NOT NULL
                THEN TO_CHAR(r.review_creation_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS review_creation_date_sk,

            CASE
                WHEN r.review_answer_timestamp IS NOT NULL
                THEN TO_CHAR(r.review_answer_timestamp::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS review_answer_date_sk,

            r.review_score::INTEGER AS review_score,

            CASE
                WHEN r.review_comment_message IS NOT NULL
                     AND TRIM(r.review_comment_message) <> ''
                THEN TRUE
                ELSE FALSE
            END AS has_comment,

            EXTRACT(EPOCH FROM (
                r.review_answer_timestamp::TIMESTAMP - r.review_creation_date::TIMESTAMP
            )) / 3600 AS response_hours

        FROM staging.order_reviews r
        LEFT JOIN staging.orders o
            ON r.order_id = o.order_id
        LEFT JOIN dwh.dim_customers dc
            ON o.customer_id = dc.customer_id;
    """
    return pd.read_sql(query, engine)

def build_fact_seller_leads(engine):
    query = """
        SELECT
            lq.mql_id,
            ds.seller_sk,
            dlo.lead_origin_sk,
            dlp.lead_profile_sk,
            dbs.business_segment_sk,

            CASE
                WHEN lq.first_contact_date IS NOT NULL
                THEN TO_CHAR(lq.first_contact_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS first_contact_date_sk,

            CASE
                WHEN lc.won_date IS NOT NULL
                THEN TO_CHAR(lc.won_date::TIMESTAMP::DATE, 'YYYYMMDD')::INTEGER
            END AS won_date_sk,

            lc.sdr_id,
            lc.sr_id,

            lc.declared_product_catalog_size::NUMERIC,
            lc.declared_monthly_revenue::NUMERIC,

            EXTRACT(EPOCH FROM (
                lc.won_date::TIMESTAMP - lq.first_contact_date::TIMESTAMP
            )) / 86400 AS days_to_close,

            CASE
                WHEN lc.mql_id IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS is_closed

        FROM staging.leads_qualified lq
        LEFT JOIN staging.leads_closed lc
            ON lq.mql_id = lc.mql_id
        LEFT JOIN dwh.dim_sellers ds
            ON lc.seller_id = ds.seller_id
        LEFT JOIN dwh.dim_lead_origin dlo
            ON lq.origin IS NOT DISTINCT FROM dlo.origin
           AND lq.landing_page_id IS NOT DISTINCT FROM dlo.landing_page_id
        LEFT JOIN dwh.dim_lead_profile dlp
            ON lc.lead_type IS NOT DISTINCT FROM dlp.lead_type
            AND lc.lead_behaviour_profile IS NOT DISTINCT FROM dlp.lead_behaviour_profile
            AND lc.business_type IS NOT DISTINCT FROM dlp.business_type
            AND lc.average_stock IS NOT DISTINCT FROM dlp.average_stock
            AND (
                    CASE
                        WHEN lc.has_company IS NULL THEN NULL
                        WHEN lc.has_company::NUMERIC = 1 THEN TRUE
                        WHEN lc.has_company::NUMERIC = 0 THEN FALSE
                        ELSE NULL
                    END
            ) IS NOT DISTINCT FROM dlp.has_company
            AND (
                    CASE
                        WHEN lc.has_gtin IS NULL THEN NULL
                        WHEN lc.has_gtin::NUMERIC = 1 THEN TRUE
                        WHEN lc.has_gtin::NUMERIC = 0 THEN FALSE
                        ELSE NULL
                    END
            ) IS NOT DISTINCT FROM dlp.has_gtin
        LEFT JOIN dwh.dim_business_segment dbs
            ON lc.business_segment = dbs.business_segment;
    """
    return pd.read_sql(query, engine)