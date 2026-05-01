# Project Architecture

## 1. System Architecture: Kimball Galaxy Schema (Fact Constellation)

The Olist business produces **five distinct business processes**, each with a different grain and measure set. A pure Star Schema (one central fact table) cannot adequately represent all of them without either blending incompatible grains or creating complex bridges. Therefore, the **Galaxy Schema** (multiple fact tables sharing conformed dimension tables) is the natural fit for this Data Warehouse.

| Reason | Explanation |
|--------|-------------|
| **Multiple business processes** | 5 independent fact tables: sales, payments, delivery, reviews, seller leads — each with its own grain |
| **Conformed dimensions** | `dim_date`, `dim_customers`, `dim_sellers` are shared across all relevant facts — the hallmark of a Galaxy Schema |
| **Query performance** | Fewer JOINs than a normalised (3NF) schema; each fact is queried independently |
| **Reporting focus** | Different analytical questions target different facts — Galaxy Schema maps naturally to this |

---

## 2. Architecture Flow Diagram

```text
┌─────────────────────┐      ┌──────────────────────┐      ┌──────────────────────────┐
│   SOURCE SYSTEM     │      │    ETL PIPELINE       │      │   TARGET: DWH SCHEMA     │
│                     │      │                       │      │                          │
│  olist.sqlite       │─────▶│  1. Extract           │      │  dim_date                │
│  ─────────────      │      │     (extract.py)      │      │  dim_geolocation         │
│  orders             │      │         │             │      │  dim_customers           │
│  customers          │      │         ▼             │      │  dim_sellers             │
│  sellers            │      │  staging.*            │      │  dim_products            │
│  products           │      │  (raw PostgreSQL)     │      │  dim_order_status        │
│  order_items        │      │         │             │      │  dim_payment_type        │
│  order_payments     │      │  2. Transform         │      │  dim_lead_origin         │
│  order_reviews      │      │     (transform.py)    │      │  dim_lead_profile        │
│  geolocation        │      │         │             │      │  dim_business_segment    │
│  leads_qualified    │      │  3. Load              │      │                          │
│  leads_closed       │      │     (load.py)         │      │  fact_order_items        │
│  product_cat...     │      │                       │─────▶│  fact_payments           │
└─────────────────────┘      └──────────────────────┘      │  fact_delivery_perf.     │
                                                            │  fact_reviews            │
                                                            │  fact_seller_leads       │
                                                            └──────────────────────────┘
```

---

## 3. Repository Directory Structure

The codebase is organized logically, separating configuration, SQL schemas, and the ETL Python scripts.

```text
week_8/
├── config/
│   ├── source_connection.py   ← SQLite connection setup
│   └── target_connection.py   ← PostgreSQL connection (SQLAlchemy)
├── docs/
│   ├── architecture.md        ← This file
│   ├── data_model.md          ← Dimensional data modeling documentation
│   ├── pipeline_design.md     ← ETL pipeline phases and details
│   ├── assumptions_and_tradeoffs.md ← Design decisions and limitations
│   └── workflow.png / pipeline_design.png ← Generated visualizations
├── etl/
│   ├── extract.py             ← Phase 1: SQLite → PostgreSQL staging
│   ├── transform.py           ← Phase 2: staging → dwh DataFrames
│   ├── load.py                ← Phase 3: DataFrames → dwh tables
│   └── pipeline.py            ← The main orchestrator (run this script)
├── sql/
│   └── create_dwh_tables.sql  ← DDL for all schemas, tables, and performance indexes
├── source/
│   └── olist.sqlite           ← Source operational database
└── requirements.txt           ← Python dependencies
```
