CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dwh;

CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_sk INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dwh.dim_geolocation (
    geolocation_sk SERIAL PRIMARY KEY,
    zip_code BIGINT NOT NULL UNIQUE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    city TEXT,
    state TEXT
);

CREATE TABLE IF NOT EXISTS dwh.dim_customers (
    customer_sk SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    customer_unique_id TEXT,
    geolocation_sk INTEGER REFERENCES dwh.dim_geolocation(geolocation_sk)
);

CREATE TABLE IF NOT EXISTS dwh.dim_sellers (
    seller_sk SERIAL PRIMARY KEY,
    seller_id TEXT NOT NULL UNIQUE,
    geolocation_sk INTEGER REFERENCES dwh.dim_geolocation(geolocation_sk)
);

CREATE TABLE IF NOT EXISTS dwh.dim_products (
    product_sk SERIAL PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_category_name TEXT,
    product_category_name_english TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);

CREATE TABLE IF NOT EXISTS dwh.dim_order_status (
    order_status_sk SERIAL PRIMARY KEY,
    order_status TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dwh.dim_payment_type (
    payment_type_sk SERIAL PRIMARY KEY,
    payment_type TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dwh.dim_lead_origin (
    lead_origin_sk SERIAL PRIMARY KEY,
    origin TEXT,
    landing_page_id TEXT,
    UNIQUE (origin, landing_page_id)
);

CREATE TABLE IF NOT EXISTS dwh.dim_lead_profile (
    lead_profile_sk SERIAL PRIMARY KEY,
    lead_type TEXT,
    lead_behaviour_profile TEXT,
    business_type TEXT,
    average_stock TEXT,
    has_company BOOLEAN,
    has_gtin BOOLEAN,
    UNIQUE (
        lead_type,
        lead_behaviour_profile,
        business_type,
        average_stock,
        has_company,
        has_gtin
    )
);

CREATE TABLE IF NOT EXISTS dwh.dim_business_segment (
    business_segment_sk SERIAL PRIMARY KEY,
    business_segment TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dwh.dim_lead_origin (
    lead_origin_sk SERIAL PRIMARY KEY,
    origin TEXT,
    landing_page_id TEXT,
    UNIQUE (origin, landing_page_id)
);

CREATE TABLE IF NOT EXISTS dwh.dim_lead_profile (
    lead_profile_sk SERIAL PRIMARY KEY,
    lead_type TEXT,
    lead_behaviour_profile TEXT,
    business_type TEXT,
    average_stock TEXT,
    has_company BOOLEAN,
    has_gtin BOOLEAN,
    UNIQUE (
        lead_type,
        lead_behaviour_profile,
        business_type,
        average_stock,
        has_company,
        has_gtin
    )
);

CREATE TABLE IF NOT EXISTS dwh.dim_business_segment (
    business_segment_sk SERIAL PRIMARY KEY,
    business_segment TEXT NOT NULL UNIQUE
);

-- **********************Fact Tables *******************
CREATE TABLE IF NOT EXISTS dwh.fact_order_items (
    order_item_sk SERIAL PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_sk INTEGER REFERENCES dwh.dim_customers(customer_sk),
    product_sk INTEGER REFERENCES dwh.dim_products(product_sk),
    seller_sk INTEGER REFERENCES dwh.dim_sellers(seller_sk),
    order_status_sk INTEGER REFERENCES dwh.dim_order_status(order_status_sk),
    purchase_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    price NUMERIC,
    freight_value NUMERIC,
    total_item_value NUMERIC
);

CREATE TABLE IF NOT EXISTS dwh.fact_payments (
    payment_sk SERIAL PRIMARY KEY,
    order_id TEXT NOT NULL,
    payment_sequential INTEGER NOT NULL,
    customer_sk INTEGER REFERENCES dwh.dim_customers(customer_sk),
    payment_type_sk INTEGER REFERENCES dwh.dim_payment_type(payment_type_sk),
    purchase_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    payment_installments INTEGER,
    payment_value NUMERIC
);

CREATE TABLE IF NOT EXISTS dwh.fact_delivery_performance (
    delivery_sk SERIAL PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    customer_sk INTEGER REFERENCES dwh.dim_customers(customer_sk),
    order_status_sk INTEGER REFERENCES dwh.dim_order_status(order_status_sk),
    purchase_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    approved_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    delivered_carrier_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    delivered_customer_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    estimated_delivery_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    approval_hours NUMERIC,
    carrier_delivery_days NUMERIC,
    customer_delivery_days NUMERIC,
    estimated_vs_actual_days NUMERIC,
    is_late BOOLEAN
);

CREATE TABLE IF NOT EXISTS dwh.fact_reviews (
    review_sk SERIAL PRIMARY KEY,
    review_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    customer_sk INTEGER REFERENCES dwh.dim_customers(customer_sk),
    review_creation_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    review_answer_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    review_score INTEGER,
    has_comment BOOLEAN,
    response_hours NUMERIC
);

CREATE TABLE IF NOT EXISTS dwh.fact_seller_leads (
    seller_lead_sk SERIAL PRIMARY KEY,

    mql_id TEXT NOT NULL UNIQUE,

    seller_sk INTEGER REFERENCES dwh.dim_sellers(seller_sk),
    lead_origin_sk INTEGER REFERENCES dwh.dim_lead_origin(lead_origin_sk),
    lead_profile_sk INTEGER REFERENCES dwh.dim_lead_profile(lead_profile_sk),
    business_segment_sk INTEGER REFERENCES dwh.dim_business_segment(business_segment_sk),

    first_contact_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),
    won_date_sk INTEGER REFERENCES dwh.dim_date(date_sk),

    sdr_id TEXT,
    sr_id TEXT,

    declared_product_catalog_size NUMERIC,
    declared_monthly_revenue NUMERIC,
    days_to_close NUMERIC,
    is_closed BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_fact_seller_leads_mql_id
ON dwh.fact_seller_leads(mql_id);

CREATE INDEX IF NOT EXISTS idx_fact_seller_leads_seller_sk
ON dwh.fact_seller_leads(seller_sk);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_order_id
ON dwh.fact_order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_customer_sk
ON dwh.fact_order_items(customer_sk);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_product_sk
ON dwh.fact_order_items(product_sk);

CREATE INDEX IF NOT EXISTS idx_fact_payments_order_id
ON dwh.fact_payments(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_delivery_order_id
ON dwh.fact_delivery_performance(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_reviews_order_id
ON dwh.fact_reviews(order_id);