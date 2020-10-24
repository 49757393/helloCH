用户配置
=======

服务配置 /etc/clickhouse-server

users.xml

安装时，给了一个口令，1234，存放的路径

/etc/clickhouse-server/users.d/default-password.xml

```xml
<yandex><users><default><password>1234</password></default></users></yandex>
```

clickhouse-client --password 1234

> echo -n 1234 | openssl dgst -sha256  
(stdin)= 03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4

```xml
<password_sha256_hex>03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4</password_sha256_hex>
```

增加一个用户hzg

```xml
<hzg>
    <password_sha256_hex>03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4</password_sha256_hex>
    <networks incl="networks" replace="replace">
        <ip>::/0</ip>
    </networks>

    <!-- Settings profile for user. -->
    <profile>default</profile>

    <!-- Quota for user. -->
    <quota>default</quota>
</hzg>
```

> clickhouse-client -u hzg --password 1234