"""
东京成交数据 CSV 数据源：从项目内 data/tokyo_transaction/（或配置路径）读取 CSV，
按区、年份过滤后返回格式化文本，供区域分析师交给大模型。
后端单独启动或部署时均生效，不依赖 .cursor。调用时打 log_skill_used 便于确认 skill 生效。
"""
import os
import re
from typing import Optional

from japanai.dataflows.config import get_config
from japanai.utils.step_logger import log_skill_used

# 区名日文 → 英文 Ward（与 skill/reference.md 一致）
WARD_JA_TO_EN = {
    "千代田区": "Chiyoda Ward",
    "中央区": "Chuo Ward",
    "港区": "Minato Ward",
    "新宿区": "Shinjuku Ward",
    "文京区": "Bunkyo Ward",
    "台東区": "Taito Ward",
    "墨田区": "Sumida Ward",
    "江東区": "Koto Ward",
    "品川区": "Shinagawa Ward",
    "目黒区": "Meguro Ward",
    "大田区": "Ota Ward",
    "世田谷区": "Setagaya Ward",
    "渋谷区": "Shibuya Ward",
    "中野区": "Nakano Ward",
    "杉並区": "Suginami Ward",
    "豊島区": "Toshima Ward",
    "北区": "Kita Ward",
    "荒川区": "Arakawa Ward",
    "板橋区": "Itabashi Ward",
    "練馬区": "Nerima Ward",
    "足立区": "Adachi Ward",
    "葛飾区": "Katsushika Ward",
    "江戸川区": "Edogawa Ward",
}

# 默认用项目内 data/，后端单独启动或部署都可用，不依赖 .cursor
DEFAULT_CSV_REL_PATH = "data/tokyo_transaction/Tokyo_20244_20253_en.csv"
MAX_ROWS = 30


def _normalize_ward(ward: str) -> Optional[str]:
    """用户可能传日文区名或英文 Ward，统一为英文 Ward。"""
    ward = (ward or "").strip()
    if not ward:
        return None
    if ward in WARD_JA_TO_EN:
        return WARD_JA_TO_EN[ward]
    if "Ward" in ward:
        return ward
    for ja, en in WARD_JA_TO_EN.items():
        if ja in ward or ward in ja:
            return en
    return ward


def _parse_year_from_timing(s: str) -> Optional[int]:
    """从 '2nd quarter 2025' 解析出年份。"""
    if not s or not isinstance(s, str):
        return None
    m = re.search(r"20\d{2}", str(s))
    return int(m.group(0)) if m else None


def get_location_data(region: str, purpose: str) -> str:
    """
    从东京成交 CSV 按区/年过滤，返回格式化文本。与 mock 同签名。
    调用时打 log_skill_used，便于后端确认 skill 生效。
    """
    log_skill_used("japan-realestate-csv", "location_data from CSV")

    try:
        import pandas as pd
    except ImportError:
        return "# 区域数据（CSV）\n- 需要安装 pandas: pip install pandas\n- 安装后区域数据将来自东京成交 CSV。"

    config = get_config()
    project_dir = config.get("project_dir", ".") or "."
    csv_rel = config.get("tokyo_transaction_csv_path") or DEFAULT_CSV_REL_PATH
    csv_path = os.path.normpath(os.path.join(project_dir, csv_rel))

    if not os.path.isfile(csv_path):
        return f"# 区域数据（CSV）\n- CSV 文件不存在: {csv_path}\n- 请将 Tokyo_20244_20253_en.csv 放到 data/tokyo_transaction/ 或修改配置 tokyo_transaction_csv_path。"

    trade_date = config.get("trade_date") or ""
    try:
        from datetime import date
        year_from_date = int(trade_date[:4]) if len(trade_date) >= 4 else date.today().year
    except Exception:
        year_from_date = None

    df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)

    col_ward = "City,Town,Ward,Village"
    col_timing = "Transaction timing"
    col_value = "Total transaction value"
    if col_ward not in df.columns or col_timing not in df.columns:
        return "# 区域数据（CSV）\n- CSV 缺少必要列，请检查文件格式。"

    df["_year"] = df[col_timing].apply(_parse_year_from_timing)

    ward_en = _normalize_ward(region)
    if ward_en:
        df = df[df[col_ward].astype(str).str.contains(re.escape(ward_en), case=False, na=False)]

    if year_from_date is not None:
        df = df[df["_year"] == year_from_date]
    else:
        df = df[df["_year"].notna()].sort_values("_year", ascending=False)

    df = df.head(MAX_ROWS)

    out_cols = [col_ward, col_timing, col_value]
    area_col = next((c for c in df.columns if "Area" in c and ("u)" in c or "m" in c)), None) or ("Area(‡u)" if "Area(‡u)" in df.columns else None)
    for c in [area_col, "Land : Price per m2", "Building : Construction year", "District", "Nearest station : Name"]:
        if c and c in df.columns:
            out_cols.append(c)
    out_cols = list(dict.fromkeys(c for c in out_cols if c in df.columns))
    df_out = df[out_cols].copy()

    if df_out.empty:
        return f"# 区域数据（CSV）\n- 区域: {region}（用途: {purpose}）\n- 未找到匹配的成交记录（区/年过滤后为空）。可检查区名或基准日。"

    table = df_out.to_string(index=False)
    return f"""# 区域数据（东京成交 CSV）

- 区域: {region}（用途: {purpose}）
- 基准年: {year_from_date or '未限定'}
- 以下为近期成交/公示数据，供分析参考。

## 成交记录（前 {len(df_out)} 条）

{table}

- 数据来源: 东京不动产成交/公示价格信息（本 skill data 目录 CSV）。
"""
