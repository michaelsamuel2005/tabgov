import pandas as pd, numpy as np, duckdb, pathlib
from tabgov import supplier

def test_supplier_assessment_matches_key():
    df, key, d0, n = supplier.simulate(); iss = supplier.assess(df, d0, n)
    for k in key:
        assert set(iss[iss.issue == k].date) == key[k], k
    mo = supplier.monthly(df, iss, d0, n)
    assert mo.on_time_rate.between(0, 1).all()

def test_mart_kpi_defined_once_and_reconciles():
    con = duckdb.connect()
    con.execute("create table raw_transactions as select * from (values (1,10,1,100,2,5.0,1,-1.0,0.0,1),(2,11,2,101,1,3.0,1,0.0,-0.5,1),(3,12,8,100,1,4.0,2,0.0,0.0,2),(3,12,8,102,0,9.0,2,0.0,0.0,2)) t(household_key,basket_id,day,product_id,quantity,sales_value,store_id,retail_disc,coupon_disc,week_no)")
    con.execute("create table raw_product as select * from (values (100,'GROCERY','MILK'),(101,'','BREAD'),(102,'DRUG','X')) t(product_id,department,commodity_desc)")
    con.execute(pathlib.Path("sql/mart.sql").read_text())
    k = con.execute("select week_no, net_sales, baskets from kpi_weekly_sales order by 1").fetchall()
    assert k == [(1, 5.0 + 3.0 - 1.5, 2), (2, 4.0, 1)]          # zero-quantity line excluded
    assert con.execute("select department from dim_product where product_id=101").fetchone()[0] == "UNKNOWN"
    assert con.execute("select count(*) from fct_sales").fetchone()[0] == 3
