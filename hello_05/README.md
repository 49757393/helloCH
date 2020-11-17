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

brch_asset_stat建表语句

CREATE TABLE brch_asset_stat_test2
(
    `org_id` String,
    `bal_date` Date,
    `agmt_name` Nullable(String),
    `paper_no` String,
    `mobile_num` Nullable(String),
    `mbs_mobile` Nullable(String),
    `qry_bal` Nullable(Decimal(18,2)),
    `fix_bal` Nullable(Decimal(18,2)),
    `gf_quot` Nullable(Decimal(18,2)),
    `fund_bal` Nullable(Decimal(18,2)),
    `ins_bal` Nullable(Decimal(18,2)),
    `servicestt` Nullable(Int32),
    `id_hy` Nullable(String),
    `phone` Nullable(String),
    `hytype` Nullable(Int32),
    `viplev` Nullable(String),
    `up_brh_code` Nullable(String)
)
ENGINE = MergeTree()
PARTITION BY bal_date
ORDER BY (paper_no, bal_date,org_id)
SETTINGS index_granularity = 8192

---clickhouse之间迁移数据 几种方式
1,利用linux管道传输大数据量数据
clickhouse-client -h 10.239.1.5 -u admin --password pydj1234    -q "SELECT * FROM finance.brch_asset_stat FORMAT CSVWithNames" | \ clickhouse-client --host 127.0.0.1  --password 123456  -q "INSERT INTO default.brch_asset_stat FORMAT CSVWithNames"
2,表数据量不大的情况下 可以通过clickhouse_client 连接后直接操作
insert into 目的数据库.表 select * from remote('数据源的ip',数据库.表,'登录名','登录密码')


clickhouse-client --password 123456    -q "SELECT up_brh_code,count(1) FROM default.brch_asset_stat group by up_brh_code"

----update语句
alter table table_name update col='' where condition
---alter修改表结构

alter table download add column `click_num` Nullable(UInt32);
修改字段
alter table user modify column user_name Nullable(String)
3.删除字段
alter table download drop column $click_num;



--物化视图
drop源表并不会同步drop物化视图 update，delete源表不会触发物化视图 只有insert会触发，同时插入的时候物化视图不会根据表结构重建数据，而是直接插入
创建物化视图后除了物化视图 还有一个inner开头的表

查看数据表分区信息
--查看测试表在19年12月的分区信息
SELECT 
    partition AS `分区`,
    sum(rows) AS `总行数`,
    formatReadableSize(sum(data_uncompressed_bytes)) AS `原始大小`,
    formatReadableSize(sum(data_compressed_bytes)) AS `压缩大小`,
    round((sum(data_compressed_bytes) / sum(data_uncompressed_bytes)) * 100, 0) AS `压缩率`
FROM system.parts
WHERE (database IN ('default')) AND (table IN ('download'))
GROUP BY partition
ORDER BY partition ASC


SELECT 
    table AS `表名`,
    sum(rows) AS `总行数`,
    formatReadableSize(sum(data_uncompressed_bytes)) AS `原始大小`,
    formatReadableSize(sum(data_compressed_bytes)) AS `压缩大小`,
    round((sum(data_compressed_bytes) / sum(data_uncompressed_bytes)) * 100, 0) AS `压缩率`
FROM system.parts
WHERE table IN ('download')
GROUP BY table

创建表
        CREATE TABLE download (
        when DateTime,
        userid UInt32,
        bytes Float32
        ) ENGINE=MergeTree
        PARTITION BY toYYYYMM(when)
        ORDER BY (userid, when)

        INSERT INTO download
        SELECT
            now() + number * 3 as when,
            25,
            rand() % 100000000
        FROM system.numbers
        LIMIT 5000000

创建物化视图
        CREATE MATERIALIZED VIEW download_daily_mv
        ENGINE = SummingMergeTree
        PARTITION BY toYYYYMM(day) ORDER BY (day)
        POPULATE
        AS SELECT
        toStartOfDay(when) AS day,
        count() as downloads,
        sum(bytes) AS bytes
        FROM download
        GROUP BY  day



ORDER BY 可以代替PRIMARY KEY

剃重表结构
create table replacing_test (date Date, id UInt8, name String,  point DateTime) 
ENGINE= ReplacingMergeTree(date, (date,id, name), 8192,point) ---date作为分区键，id和name作为联合主键，point可以理解为版本号

INSERT INTO replacing_test(date , id , name ,  point ) values('2020-11-01',1,'a',now())('2020-11-01',2,'a',now());
OPTIMIZE TABLE replacing_test
因此将资产表的表结构改成 需要新增
CREATE TABLE brch_asset_stat_test4
(
    `org_id` String,
    `bal_date` Date,
    `agmt_name` Nullable(String),
    `paper_no` String,
    `mobile_num` Nullable(String),
    `mbs_mobile` Nullable(String),
    `qry_bal` Nullable(Decimal(18,2)),
    `fix_bal` Nullable(Decimal(18,2)),
    `gf_quot` Nullable(Decimal(18,2)),
    `fund_bal` Nullable(Decimal(18,2)),
    `ins_bal` Nullable(Decimal(18,2)),
    `servicestt` Nullable(Int32),
    `id_hy` Nullable(String),
    `phone` Nullable(String),
    `hytype` Nullable(Int32),
    `viplev` Nullable(String),
    `up_brh_code` Nullable(String),
    `oper_time` DateTime
)
ENGINE = ReplacingMergeTree(bal_date,(bal_date,paper_no,org_id), 8192,oper_time)

select max(b.qry_bal-a.fix_bal),paper_no from  (select paper_no,fix_bal from  brch_asset_stat_test4 WHERE org_id='3699956Q' and bal_date='2020-10-16') a,  (select paper_no,qry_bal from  brch_asset_stat_test4 WHERE org_id='3699956Q' and bal_date='2020-11-15') b where a.paper_no  = b.paper_no