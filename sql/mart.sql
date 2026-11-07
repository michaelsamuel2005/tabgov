-- Retail mart over Complete Journey style transactions. Portable SQL (DuckDB and Snowflake).
-- raw_transactions(household_key, basket_id, day, product_id, quantity, sales_value, store_id, retail_disc, coupon_disc, week_no)
-- raw_product(product_id, department, commodity_desc)
CREATE OR REPLACE VIEW fct_sales AS
SELECT basket_id, household_key, store_id, product_id, week_no, day, quantity, sales_value,
       -(COALESCE(retail_disc,0) + COALESCE(coupon_disc,0)) AS discount
FROM raw_transactions WHERE quantity <> 0;

CREATE OR REPLACE VIEW dim_product AS
SELECT product_id, COALESCE(NULLIF(department,''),'UNKNOWN') AS department, commodity_desc FROM raw_product;

-- Governed KPI table: "Net Sales" = sales_value - discount, defined once; Tableau reads this, never recalculates.
CREATE OR REPLACE VIEW kpi_weekly_sales AS
SELECT week_no, SUM(sales_value) - SUM(discount) AS net_sales, SUM(sales_value) AS gross_sales,
       COUNT(DISTINCT basket_id) AS baskets,
       (SUM(sales_value) - SUM(discount)) / COUNT(DISTINCT basket_id) AS basket_size
FROM fct_sales GROUP BY week_no;
