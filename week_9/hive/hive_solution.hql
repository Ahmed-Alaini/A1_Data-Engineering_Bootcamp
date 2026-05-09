-- =================================================================================
-- HIVE LAB SOLUTION SCRIPT
-- =================================================================================
-- Execute this script in your Hive environment to satisfy the lab requirements.
-- Make sure the CSV files are available in your local path or upload them to HDFS first.

-- Create a database to hold our lab tables to keep things clean
CREATE DATABASE IF NOT EXISTS hive_lab;
USE hive_lab;

-- =================================================================================
-- TASK 1: Internal vs External Tables & Handling Delimiters inside Quotes
-- =================================================================================
-- Issue: The Address column contains commas within quotes (e.g., "323 Yoder Place, NM").
-- Solution: We use org.apache.hadoop.hive.serde2.OpenCSVSerde. This SerDe natively
-- understands CSV quoting and escaping, preventing the address from being split into
-- multiple columns.

-- 1. Create Internal Table
CREATE TABLE IF NOT EXISTS internal_customer (
    customer_id STRING,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date STRING,
    start_date STRING,
    end_date STRING,
    is_current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- Load data into the internal table
-- Assuming the file is accessible locally to the Hive CLI/Beeline
LOAD DATA LOCAL INPATH 'customer_scd2_mixed.csv' INTO TABLE internal_customer;


-- 2. Create External Table
-- External tables require an explicit HDFS LOCATION. The data is managed outside Hive.
CREATE EXTERNAL TABLE IF NOT EXISTS external_customer (
    customer_id STRING,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date STRING,
    start_date STRING,
    end_date STRING,
    is_current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/hive/external_customer_data'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Load data into the external table
LOAD DATA LOCAL INPATH 'customer_scd2_mixed.csv' INTO TABLE external_customer;

-- =================================================================================
-- TASK 2: DROPPING TABLES BEHAVIOR
-- =================================================================================
-- Uncomment these lines to test the drop behavior:

-- DROP TABLE internal_customer;
-- RESULT: Hive deletes BOTH the table metadata in the metastore AND the actual data file in HDFS.
-- Data is completely gone.

-- DROP TABLE external_customer;
-- RESULT: Hive deletes ONLY the table metadata. The underlying data inside 
-- /user/hive/external_customer_data remains safely intact in HDFS.


-- =================================================================================
-- TASK 3: Slowly Changing Dimension (SCD) Type 2 (Without Transactional Tables)
-- =================================================================================
-- Hive does not support standard UPDATE or DELETE statements on non-ACID tables.
-- To track history (SCD Type 2), we use an 'INSERT OVERWRITE' pattern combining unchanged,
-- expired, and new records using a UNION ALL.

-- 1. Create the main SCD2 Dimension Table
CREATE TABLE IF NOT EXISTS customer_dim (
    customer_id STRING,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date STRING,
    start_date STRING,
    end_date STRING,
    is_current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- Load the initial mixed state data
LOAD DATA LOCAL INPATH 'customer_scd2_mixed.csv' INTO TABLE customer_dim;

-- 2. Create the Staging table for incoming updates
CREATE TABLE IF NOT EXISTS customer_updates_staging (
    customer_id STRING,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- Load the new/updated incoming records
LOAD DATA LOCAL INPATH 'customer_updated.csv' INTO TABLE customer_updates_staging;

-- 3. Perform the SCD Type 2 Merge using INSERT OVERWRITE
-- We completely overwrite customer_dim with a combination of 4 result sets:

INSERT OVERWRITE TABLE customer_dim
SELECT * FROM (

    -- A. Unchanged records: Customers who have NO new updates in the staging table.
    SELECT 
        d.customer_id, d.name, d.email, d.phone_number, d.address, d.join_date, 
        d.start_date, d.end_date, d.is_current
    FROM customer_dim d
    LEFT JOIN customer_updates_staging u ON d.customer_id = u.customer_id
    WHERE u.customer_id IS NULL

    UNION ALL

    -- B. Historical records: Past history records of customers who DO have new updates.
    -- (We must preserve their old history rows exactly as they were).
    SELECT 
        d.customer_id, d.name, d.email, d.phone_number, d.address, d.join_date, 
        d.start_date, d.end_date, d.is_current
    FROM customer_dim d
    JOIN customer_updates_staging u ON d.customer_id = u.customer_id
    WHERE d.is_current = '0'

    UNION ALL

    -- C. Expired records: The currently active record of a customer who is being updated.
    -- (We retire this row by setting end_date to today, and is_current to 0).
    SELECT 
        d.customer_id, d.name, d.email, d.phone_number, d.address, d.join_date, 
        d.start_date, 
        current_date() as end_date, -- Expire the old record today
        '0' as is_current           -- Mark as no longer current
    FROM customer_dim d
    JOIN customer_updates_staging u ON d.customer_id = u.customer_id
    WHERE d.is_current = '1'

    UNION ALL

    -- D. New incoming updates: The fresh records from the staging table.
    -- (Insert them as the new active versions).
    SELECT 
        u.customer_id, u.name, u.email, u.phone_number, u.address, u.join_date, 
        current_date() as start_date, -- Start date is today
        NULL as end_date,             -- No end date yet
        '1' as is_current             -- Mark as the current active record
    FROM customer_updates_staging u

) scd2_merge;

-- =================================================================================
-- VERIFICATION
-- =================================================================================
-- Check the results of a specific updated customer to see the history tracked
-- SELECT * FROM customer_dim WHERE customer_id = '12346';
