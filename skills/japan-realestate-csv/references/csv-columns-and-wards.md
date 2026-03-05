# 东京成交 CSV 列说明与区名映射

## CSV 列名与含义

| 列名 | 含义 | 用途 |
|------|------|------|
| Type | 土地/建物类型 | 筛选住宅/商业等 |
| Prefecture | 都道府县 | 固定 Tokyo |
| City,Town,Ward,Village | 区市町村（英文） | 按区过滤，需与用户输入的日文区名映射 |
| District | 丁目/片区 | 更细地段 |
| Nearest station : Name | 最近站名 | 按站过滤 |
| Nearest station : Distance | 到站距离（分） | 交通 |
| Total transaction value | 成交总价（日元） | 核心数值 |
| Area(‡u) | 面积（m²，‡u 表示 m²） | 单价等计算 |
| Land : Price per m2 | 土地单价（日元/m²） | 地价参考 |
| Building : Construction year | 建物竣工年 | 年代筛选 |
| Transaction timing | 如 "2nd quarter 2025" | 按年/季度过滤 |

## 区名映射（日文 → 英文 Ward）

| 日文 | 英文 (City,Town,Ward,Village) |
|------|-------------------------------|
| 千代田区 | Chiyoda Ward |
| 中央区 | Chuo Ward |
| 港区 | Minato Ward |
| 新宿区 | Shinjuku Ward |
| 文京区 | Bunkyo Ward |
| 台東区 | Taito Ward |
| 墨田区 | Sumida Ward |
| 江東区 | Koto Ward |
| 品川区 | Shinagawa Ward |
| 目黒区 | Meguro Ward |
| 大田区 | Ota Ward |
| 世田谷区 | Setagaya Ward |
| 渋谷区 | Shibuya Ward |
| 中野区 | Nakano Ward |
| 杉並区 | Suginami Ward |
| 豊島区 | Toshima Ward |
| 北区 | Kita Ward |
| 荒川区 | Arakawa Ward |
| 板橋区 | Itabashi Ward |
| 練馬区 | Nerima Ward |
| 足立区 | Adachi Ward |
| 葛飾区 | Katsushika Ward |
| 江戸川区 | Edogawa Ward |

## 配置项

- **tokyo_transaction_csv_path**：CSV 路径，相对 `project_dir`。默认：`data/tokyo_transaction/Tokyo_20244_20253_en.csv`。
- **trade_date**：分析基准日（yyyy-mm-dd），用于按年过滤；由请求传入并在 propagate 时写入 config。
