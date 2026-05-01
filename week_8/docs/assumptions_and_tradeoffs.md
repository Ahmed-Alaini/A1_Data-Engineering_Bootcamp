# Architectural Postmortem: Assumptions & Trade-offs

This document outlines the core premises and strategic compromises made while architecting the Olist Data Warehouse. Building a robust analytical environment requires balancing historical accuracy, query performance, and system complexity.

---

## Part 1: Foundational Data Assumptions

When dealing with the source OLTP data, we encountered several inconsistencies and limitations. We proceeded with the following assumptions:

1. **Geographic History Limitation:** The source system only tracks the *current* zip code for buyers and sellers. Without a historical address log, we assume this current location is valid for all past transactions.
2. **Exclusion of Precise Coordinates:** The `geolocation` dataset has an average variance of ~15.7 km per zip code. Because this level of accuracy is insufficient for exact distance calculations, we discard latitude and longitude entirely and rely on broader city/state aggregates for spatial analysis.
3. **Handling Review Duplication:** Some reviews map to multiple order items, causing duplicate `review_id`s. Rather than forcing artificial deduplication, we link distinct order constraints to a single `dim_review_comment` entity, treating the combination of `review_id` and `order_id` as the true unique identifier.
4. **Resolving Missing Sellers:** Over half of the closed leads lack a matching record in the `sellers` table. To preserve this valuable funnel data, we assign these orphaned records to a generic 'Unknown' seller profile (mapped to a default surrogate key).
5. **Incomplete Translations:** A few product categories lack English equivalents in the lookup table. We assume these gaps will be handled manually prior to the ETL process and that the rest of the mapping is complete.
6. **Preservation of Zero-Dollar Transactions:** We observed a handful of payments with a value of 0. Assuming these are valid promotional vouchers, we retain them in the pipeline but flag them explicitly using an `is_zero_value` indicator.
7. **Exclusion of Incomplete Orders:** Orders marked as `canceled` or `created` are dropped from the fulfillment metrics, under the assumption that these states are terminal and will not eventually transition to `delivered`.
8. **City Naming Discrepancies:** Minor spelling differences exist between customer cities and geolocation cities. We trust the customer's input as the source of truth and normalize the geolocation records to match.

---

## Part 2: Architectural Decisions & Compromises

Every design choice carries a trade-off. Below are the primary decisions made to optimize the warehouse for analytical workloads.

### 1. Decoupling Fact Tables
* **The Decision:** We built five distinct fact tables instead of a single, massive order-level table.
* **The Rationale:** Mixing different granularities (e.g., individual payment installments vs. overall order fulfillment) into one table leads to severe data duplication and aggregation errors.
* **The Compromise:** It requires analysts to write more JOINs and manage more tables, but it guarantees mathematically accurate metrics and faster, narrower queries.

### 2. Zip-Code Level Granularity
* **The Decision:** `dim_location` uses zip codes, cities, and states, but omits GPS coordinates entirely.
* **The Rationale:** The source coordinates are too unreliable for geospatial math. Attempting to use them would introduce data quality warnings for no analytical gain.
* **The Compromise:** We sacrifice map-based visualizations and exact distance calculations in favor of data integrity.

### 3. Overwriting Entity Demographics (SCD Type 1)
* **The Decision:** We update customer and seller dimensions in place, keeping only their most recent demographic state.
* **The Rationale:** Most analytics focus on the *current* status of the user. Past transaction locations are already safely stored in the fact tables.
* **The Compromise:** We cannot easily reconstruct a user's profile exactly as it was three years ago, but we save significant ETL complexity.

### 4. Tracking Product History (SCD Type 2)
* **The Decision:** Changes to product categories trigger a new row with validity dates (SCD Type 2).
* **The Rationale:** Revenue reporting by category is highly sensitive; retroactively changing a product's category would ruin historical financial time-series reports.
* **The Compromise:** Results in a larger product dimension table and much more complex update logic compared to SCD Type 1.

### 5. Redundant Keys in Payment and Review Facts
* **The Decision:** We include the `customer_key` directly in the payment and review facts, even though it could technically be fetched by joining the sales table via `order_id`.
* **The Rationale:** It drastically simplifies querying. A single payment or review is unambiguously tied to one customer, so we remove the need for a complex bridge join.
* **The Compromise:** Costs a few extra bytes per row, which is easily mitigated by modern columnar database compression.

### 6. Omitting Sellers from Fulfillment Tracking
* **The Decision:** `fact_order_fulfillment` does not contain a `seller_key`.
* **The Rationale:** Orders often contain items from multiple sellers. Assigning an entire order's delivery performance to a single seller would be factually incorrect and distort metrics.
* **The Compromise:** Finding a specific seller's average delivery time requires joining back to the sales fact, adding slight query friction to ensure accuracy.

### 7. Calculating Metrics at Load Time
* **The Decision:** We compute days to deliver, lateness, and delivery status during the ETL process, storing them as physical columns.
* **The Rationale:** These are the most frequently queried metrics. Calculating date math on the fly would bottleneck the BI reporting layer.
* **The Compromise:** Slightly inflates storage requirements and slows down the ETL process, but provides massive query performance benefits downstream.

### 8. Handling Duplicates and Updates
* **The Decision:** Most fact tables use `ON CONFLICT DO NOTHING` to ignore duplicate inserts, while the fulfillment fact uses an UPSERT to update existing records.
* **The Rationale:** Static historical data shouldn't change, so ignoring duplicates is safest. Fulfillment, however, requires updates as orders transition from shipped to delivered across different ETL runs.
* **The Compromise:** Any actual errors loaded into static fact tables require a manual wipe and reload, rather than auto-correcting seamlessly.

### 9. Timestamp-Based Extraction
* **The Decision:** We rely on a `last_extracted` watermark timestamp to pull new data.
* **The Rationale:** It's a simple, transparent method to handle both full snapshots and incremental loads.
* **The Compromise:** If source system clocks are wrong or records are backdated, data might be skipped. A log-based CDC would be better for true production systems.

### 10. Relying Exclusively on Indexes
* **The Decision:** We skipped table partitioning entirely, relying only on standard indexes.
* **The Rationale:** The dataset is under a million rows, making partitioning an unnecessary engineering overhead.
* **The Compromise:** If data volume suddenly spikes to tens of millions of rows, we will have to retrofit range partitioning later.

### 11. Pushing Continuous Variables to Facts
* **The Decision:** Continuous metrics like `declared_monthly_revenue` were moved out of the lead dimension and placed directly into the fact table.
* **The Rationale:** Dimensions are meant for grouping (e.g., revenue bands), not storing infinite continuous numbers, which bloat the dimension and complicate surrogate key generation.
* **The Compromise:** Makes the fact table slightly wider but strictly adheres to Kimball data modeling best practices.
