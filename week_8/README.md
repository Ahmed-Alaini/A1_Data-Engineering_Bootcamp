# Olist E-Commerce Data Warehouse

## 1. Project Overview

**Dataset:** Olist Brazilian E-Commerce (SQLite format)  
**Target:** PostgreSQL Data Warehouse  
**Tools:** Python 3, pandas, SQLAlchemy, psycopg2, PostgreSQL

The Olist dataset represents a Brazilian e-commerce marketplace. It contains data about orders, customers, sellers, products, payments, reviews, and seller acquisition (leads). The goal is to transform this operational data into a queryable analytical data warehouse.

## 2. Data Warehouse Model

![Data Model ERD](docs/images/ERD_DWH.png)

## 3. Pipeline Design

![Pipeline Design](docs/images/pipeline_design.png)

## 4. Brief of Architecture

The project uses a **Kimball Galaxy Schema (Fact Constellation)**. The Olist business produces five distinct business processes, each with a different grain and measure set. A pure Star Schema (one central fact table) cannot adequately represent all of them. The Galaxy Schema uses multiple fact tables sharing conformed dimension tables.

```text
PostgreSQL Database: olist_dwh
│
├── staging.*       ← Raw copies of all SQLite source tables
│
└── dwh.*           ← Dimensional model (Galaxy Schema / Fact Constellation)
    ├── Dimensions  (10 tables)
    └── Facts       (5 tables)
```


## 5. Repository Architecture

```text
week_8/
├── config/
│   ├── source_connection.py   ← SQLite connection
│   └── target_connection.py   ← PostgreSQL connection (SQLAlchemy)
├── etl/
│   ├── extract.py             ← Phase 1: SQLite → PostgreSQL staging
│   ├── transform.py           ← Phase 2: staging → dwh DataFrames
│   ├── load.py                ← Phase 3: DataFrames → dwh tables
│   └── pipeline.py            ← Orchestrator (run this)
├── sql/
│   └── create_dwh_tables.sql  ← DDL for all schemas, tables, indexes
├── source/
│   └── olist.sqlite           ← Source database
└── requirements.txt
```

## 6. Features

* **End-to-End ETL Pipeline:** Automated extraction from SQLite, data transformation using Python/Pandas, and bulk loading into PostgreSQL.
* **Dimensional Modeling:** Implemented a Galaxy Schema with 5 fact tables (sales, payments, delivery, reviews, seller leads) and 10 conformed dimensions.
* **Performance Optimizations:** Uses chunked extraction to handle memory constraints and comprehensive indexing on all foreign keys.
* **Idempotent Operations:** Pipeline design ensures safe re-runs with Truncate-and-Reload strategies.
* **Analytical Ready:** Structure enables high-performance queries for sales trending, customer lifetime value, and logistics performance.

## 7. Key Design Decisions

* **Galaxy Schema over Star Schema:** Avoids fan-out aggregation errors that would occur from mixing different business process grains in one table.
* **Separate Fact Tables:** Payments and order items have different grains and are thus separated to prevent many-to-many bridge complexities.
* **Pre-computed Metrics:** Computed columns (e.g., `total_item_value`, `is_late`) are stored directly in fact tables to eliminate repeated computation during analysis.
* **Chunked Extraction:** Data is extracted in manageable chunks (e.g., 50k rows) to prevent out-of-memory errors on large tables.
* **Integer Date Surrogate Keys:** `YYYYMMDD` integers are used for date keys to optimize filtering performance and self-documenting readability.
