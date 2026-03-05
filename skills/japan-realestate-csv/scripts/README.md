# scripts

本目录存放本 skill 的可执行脚本。

- **query_csv.py**：按区/年/片区/站过滤东京成交 CSV，输出表格或 JSON。默认读项目根 `data/tokyo_transaction/`。用法：`python3 query_csv.py [--csv PATH] [--ward "Chuo Ward"] [--year 2025] [--limit 30]`。
