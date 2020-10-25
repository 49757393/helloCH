clickhouse的sql是区分大小写的

创建数据库
========

CREATE DATABASE IF NOT EXISTS finance;

创建Memory表
===========

CREATE TABLE finance.brch_qry_dtl (
    acc String,
    tran_date Date,
    amt Decimal(10, 2),
    dr_cr_flag Int,
    rpt_sum String,
    timestamp1 String
) ENGINE = Memory;

SHOW DATABASES;
USE finance;
SHOW TABLES;
DESC brch_qry_dtl;

DROP TABLE brch_qry_dtl;

创建MergeTree表
==============

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

字段定义的次序，对应data.csv的顺序

改变PARTITION

CREATE TABLE finance.brch_qry_dtl (
    tran_date Date,
    timestamp1 String,
    acc String,
    amt Decimal(10, 2),
    dr_cr_flag Int,
    rpt_sum String
) ENGINE = MergeTree
PARTITION BY toYYYYMM(tran_date)
ORDER BY acc;

导入数据
=======

> cat ./data-files/data.csv | clickhouse-client -u hzg --password 1234 --database=finance --query="INSERT INTO brch_qry_dtl FORMAT CSV";

Clickhouse 批量插入报错：Too many partitions for single INSERT block (more than 100)

参考资料: https://www.jianshu.com/p/8aa2a20ab00a

在users.xml配置文件中进行配置。配置在 <profiles>块中, max_partitions_per_insert_block, 设置为0

\<profiles\>中，mytest继承default

```xml
<mytest>
    <profile>default</profile>
    <max_partitions_per_insert_block>0</max_partitions_per_insert_block>
</mytest>
```

\<users\>中，\<hzg\>增加

```xml
<profile>mytest</profile>
```

经过上述配置后，导入成功

> clickhouse-client -u hzg --password 1234 --database=finance

```sql
SELECT COUNT(*) FROM brch_qry_dtl where tran_date='2019-11-27';
SELECT SUM(amt) FROM brch_qry_dtl where tran_date='2019-11-27' AND dr_cr_flag=1;
SELECT rpt_sum, SUM(amt) FROM brch_qry_dtl where tran_date='2019-11-27' AND dr_cr_flag=1 GROUP BY rpt_sum;
```