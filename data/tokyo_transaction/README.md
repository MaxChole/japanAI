# 东京成交数据（日本房产 skill 用）

后端 **默认从这里读取** `Tokyo_20244_20253_en.csv`，不依赖 `.cursor` 目录。

- 后端单独启动或部署时，只要项目根正确、此目录存在且含 CSV，skill 即生效。
- 若 CSV 放在别处，在配置中设置 `tokyo_transaction_csv_path` 即可。
