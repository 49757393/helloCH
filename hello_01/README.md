安装
===

参考资料 https://clickhouse.tech/docs/en/getting-started/install/

clickhouse 充分利用cpu硬件资源

grep -q sse4_2 /proc/cpuinfo && echo "SSE 4.2 supported" || echo "SSE 4.2 not supported"

手动安装

Packages  
1. clickhouse-common-static — Installs ClickHouse compiled binary files.
2. clickhouse-server — Creates a symbolic link for clickhouse-server and installs the default server configuration.
3. clickhouse-client — Creates a symbolic link for clickhouse-client and other client-related tools. and installs client configuration files.
4. clickhouse-common-static-dbg — Installs ClickHouse compiled binary files with debug info.

依次序安装

https://repo.clickhouse.tech/deb/stable/main/

下载deb包: clickhouse-common-static, clickhouse-server, clickhouse-client