# japanAI 每日更新记录

**说明**：每次本项目提交（commit）前，请在本文档追加当日修改与完成事项；以后每次提交都需在此记录每日事情，便于追溯。

---

## 2025-03-05（今日）

### 修改与完成事项

- **日本房产数据 Skill（japan-realestate-csv）**
  - 将 skill 从 `.cursor/skills/` 迁出至项目内 `skills/japan-realestate-csv/`，**不再与 Cursor 绑定**，明确为「用户与 japanAI 大模型」之间的能力。
  - 按标准格式整理 skill 目录：`SKILL.md` + `references/` + `scripts/` + `assets/`。
  - **references/**：新增 `references/csv-columns-and-wards.md`（CSV 列说明、区名映射、配置项）、`references/README.md`。
  - **scripts/**：保留 `query_csv.py`，新增 `scripts/README.md`；脚本默认读项目根 `data/tokyo_transaction/`。
  - **assets/**：新增目录及 `assets/README.md`，说明静态资源用途；实际 CSV 仍在项目根 `data/tokyo_transaction/`。
  - 删除根目录旧版 `reference.md`，内容已迁入 `references/csv-columns-and-wards.md`。

- **数据与配置**
  - 后端默认 CSV 路径改为 `data/tokyo_transaction/Tokyo_20244_20253_en.csv`（相对项目根），**不依赖 .cursor**，后端单独启动或部署均生效。
  - 已创建 `data/tokyo_transaction/` 并放入 CSV，新增 `data/tokyo_transaction/README.md`。
  - `default_config.py`、`csv_vendor.py` 中默认路径与错误提示均指向 `data/tokyo_transaction/`。

- **Skill 行为**
  - **自动触发**：`get_location_data` 不再读取「是否用 CSV」配置，仅根据请求区域判断；若为东京/日本相关（含 东京、港区、中央区、千代田区、Tokyo、Minato 等关键词）则自动走 CSV，否则 mock。无人为开关。
  - **日志**：skill 生效时打 `log_skill_used("japan-realestate-csv", ...)`，便于后端确认（如 `get_location_data → CSV (skill 自动触发)`、`location_data from CSV`）。

- **其他**
  - 从 `data_vendors` 中移除 `location_data` 配置项（由 skill 自动路由，不再通过配置选择 csv/mock）。
  - 新增本文档 `docs/DAILY_LOG.md`，约定每次提交前在此追加当日更新。
