# Hive Lab Assignment Explanation

This document explains the concepts and solutions implemented in the `hive_solution.hql` script to solve the lab assignment tasks.

## 1. Handling Delimiters Inside Columns
**The Problem:** The `customer_scd2_mixed.csv` file uses commas (`,`) to separate columns. However, the `Address` column contains commas within the data itself (e.g., `"323 Yoder Place East Katherinemouth, NM 43638"`). A standard Hive `RowFormat Delimited` would incorrectly split the address into multiple columns.

**The Solution:** We used `org.apache.hadoop.hive.serde2.OpenCSVSerde`. This SerDe is specifically designed to handle CSV formatting correctly. By defining the `quoteChar = "\""`, Hive knows to ignore any commas that are placed inside double quotes, keeping the full address inside a single column.

---

## 2. Internal vs. External Tables
The assignment asked to drop both types of tables and observe what happens to the data. 

**Internal Tables (Managed by Hive):**
- When you create an internal table, Hive takes full ownership of both the **metadata** (table schema in the metastore) and the **actual data files** in HDFS.
- **When Dropped:** If you run `DROP TABLE internal_customer`, the data file in HDFS is permanently deleted along with the table definition. 

**External Tables (Managed by User):**
- External tables point to an existing HDFS `LOCATION`. Hive only manages the metadata.
- **When Dropped:** If you run `DROP TABLE external_customer`, Hive only deletes the table definition from its metastore. The underlying CSV data files in HDFS remain completely untouched and safe.

---

## 3. Slowly Changing Dimension (SCD Type 2) in Hive
**The Problem:** Standard Hive tables (non-transactional/non-ACID) do not support `UPDATE` or `DELETE` SQL commands. However, an SCD Type 2 dimension requires us to "retire" old records (set an end date) and "insert" new records to track historical changes.

**The Solution:** To get around the lack of `UPDATE`, we use an **INSERT OVERWRITE** pattern combined with a `UNION ALL`. We take the base `customer_dim` table and completely overwrite it with a new combined dataset constructed from four parts:

1. **Unchanged Records:** Customers who didn't get an update are kept exactly as they are. *(Found using a LEFT JOIN where staging is null)*.
2. **Old History Records:** The past, already-expired versions of customers who are receiving new updates today. We must preserve their historical rows. *(Found where `is_current = '0'`)*.
3. **Expired Records:** The currently active versions of customers who are receiving an update today. We "retire" them by selecting them, replacing their `end_date` with today's date, and setting `is_current = '0'`.
4. **New Updates:** The brand-new data coming from `customer_updated.csv`. We select these rows, set their `start_date` to today, `end_date` to NULL, and `is_current = '1'`.

By unioning these 4 streams together and overwriting the table, we perfectly simulate an `UPDATE` and successfully implement SCD Type 2 history tracking!
