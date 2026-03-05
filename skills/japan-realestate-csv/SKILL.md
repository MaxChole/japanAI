---
name: japan-realestate-csv
description: When the user queries Japanese or Tokyo real estate data via japanAI, the system reads Tokyo transaction CSV from project data folder, filters by year and location, and passes the figures to japanAI's model. This skill is between the user and the japanAI model, not tied to any editor.
---

# Japan Real Estate CSV Skill

本技能是 **用户与 japanAI 大模型** 之间的能力：用户通过 japanAI（API/前端）查询日本/东京房产时，系统自动读项目内东京成交 CSV，按年份与地理位置过滤后，将准确数据交给 japanAI 的分析师模型生成报告。与编辑器无关，skill 仅属于 japanAI 应用。

## 目录结构（标准格式）

```
skills/japan-realestate-csv/
├── SKILL.md           # 本说明
├── references/        # 参考文档
├── scripts/           # 可执行脚本
└── assets/            # 静态资源
```

- **references/**：CSV 列说明、区名映射、配置项等，见 [references/csv-columns-and-wards.md](references/csv-columns-and-wards.md)。
- **scripts/**：如 `query_csv.py`，按区/年过滤 CSV 并输出，见 [scripts/README.md](scripts/README.md)。
- **assets/**：本 skill 的静态资源（若有）；实际 CSV 数据在项目根 `data/tokyo_transaction/`。

## 何时触发（自动触发，无需任何配置）

- 用户请求涉及日本/东京房产时（区域含 东京、港区、中央区、千代田区、Tokyo、Minato 等），**skill 自动触发**：系统读 `data/tokyo_transaction/` 下 CSV、把数据交给大模型。
- **不需要**也**没有**「要不要用 CSV」的配置：东京/日本相关即读 CSV 给大模型；非东京/日本则用通用数据。

## 行为

1. **CSV 路径**：后端默认读 `data/tokyo_transaction/Tokyo_20244_20253_en.csv`（相对项目根），可配置 `tokyo_transaction_csv_path`。
2. **读取与过滤**：按区域（区名映射见 references）、基准日年份（`trade_date`）过滤，取当年或最近 1–2 年记录，最多前 N 条（如 30）。
3. **交给大模型**：将过滤结果格式化为表格或结构化文本，作为 `get_location_data` 的工具返回值交给区域分析师 LLM。

## 配置与路径

- **数据目录**：`data/tokyo_transaction/`（项目根下），后端单独启动或部署均生效。
- **配置项**：`tokyo_transaction_csv_path` 指向 CSV；`trade_date` 由请求传入。无「是否使用 CSV」配置。

## 日志

skill 生效时后端输出：`[JapanAI] Skill 生效: japan-realestate-csv | ...`，便于确认。
