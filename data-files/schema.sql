CREATE DATABASE IF NOT EXISTS finance;

CREATE TABLE finance.brch_qry_dtl (
    acc String,
    tran_date Date,
    amt Decimal(10, 2),
    dr_cr_flag Int,
    rpt_sum String,
    timestamp1 String
) ENGINE = Memory;

CREATE TABLE finance.brch_qry_dtl (
    tran_date Date,
    timestamp1 String,
    acc String,
    amt Decimal(10, 2),
    dr_cr_flag Int,
    rpt_sum String
) ENGINE = MergeTree
PARTITION BY acc
ORDER BY (tran_date, timestamp1);