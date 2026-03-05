#!/usr/bin/env python3
"""
按区/年/片区/站过滤东京成交 CSV，输出表格或 JSON。默认读项目根 data/tokyo_transaction/。
用法: python3 query_csv.py [--csv PATH] [--ward "Chuo Ward"] [--year 2025] [--limit 30]
"""
import argparse
import json
import os
import re
import sys

# 区名日文 → 英文 Ward（与 reference.md 一致）
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


def normalize_ward(ward: str) -> str:
    """用户可能传日文区名或英文 Ward，统一为英文 Ward。"""
    ward = (ward or "").strip()
    if not ward:
        return ""
    if ward in WARD_JA_TO_EN:
        return WARD_JA_TO_EN[ward]
    if "Ward" in ward:
        return ward
    for ja, en in WARD_JA_TO_EN.items():
        if ja in ward or ward in ja:
            return en
    return ward


def parse_year_from_timing(s: str) -> int | None:
    """从 '2nd quarter 2025' 解析出年份。"""
    if not s or not isinstance(s, str):
        return None
    m = re.search(r"20\d{2}", s)
    return int(m.group(0)) if m else None


def main():
    parser = argparse.ArgumentParser(description="Filter Tokyo transaction CSV by ward/year/etc.")
    # 默认用项目根 data/tokyo_transaction/（与后端一致）
    cwd_csv = os.path.join(os.getcwd(), "data", "tokyo_transaction", "Tokyo_20244_20253_en.csv")
    default_csv = cwd_csv
    parser.add_argument("--csv", default=default_csv, help="Path to CSV (default: project data/tokyo_transaction/)")
    parser.add_argument("--ward", help="Ward name (EN or JP, e.g. Chuo Ward, 中央区)")
    parser.add_argument("--year", type=int, help="Filter by year (from Transaction timing)")
    parser.add_argument("--district", help="District name (partial match)")
    parser.add_argument("--station", help="Nearest station name (partial match)")
    parser.add_argument("--limit", type=int, default=30, help="Max rows to output")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    try:
        import pandas as pd
    except ImportError:
        print("pandas required: pip install pandas", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.csv):
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(args.csv, encoding="utf-8", low_memory=False)
    col_ward = "City,Town,Ward,Village"
    col_timing = "Transaction timing"
    col_value = "Total transaction value"
    col_area = next((c for c in df.columns if "Area" in c), None)
    col_land = "Land : Price per m2" if "Land : Price per m2" in df.columns else None
    col_year_build = "Building : Construction year" if "Building : Construction year" in df.columns else None
    col_district = "District" if "District" in df.columns else None
    col_station = "Nearest station : Name" if "Nearest station : Name" in df.columns else None

    if col_ward not in df.columns or col_timing not in df.columns:
        print("Required columns missing", file=sys.stderr)
        sys.exit(1)

    df["_year"] = df[col_timing].apply(parse_year_from_timing)

    ward_en = normalize_ward(args.ward) if args.ward else ""
    if ward_en:
        df = df[df[col_ward].astype(str).str.contains(re.escape(ward_en), case=False, na=False)]

    if args.year is not None:
        df = df[df["_year"] == args.year]

    if args.district and col_district:
        df = df[df[col_district].astype(str).str.contains(re.escape(args.district), case=False, na=False)]
    if args.station and col_station:
        df = df[df[col_station].astype(str).str.contains(re.escape(args.station), case=False, na=False)]

    df = df.head(args.limit)
    out_cols = [col_ward, col_timing, col_value]
    if col_area:
        out_cols.append(col_area)
    if col_land:
        out_cols.append(col_land)
    if col_year_build:
        out_cols.append(col_year_build)
    if col_district:
        out_cols.append(col_district)
    if col_station:
        out_cols.append(col_station)
    out_cols = [c for c in out_cols if c in df.columns]
    df_out = df[out_cols].copy()

    if args.format == "json":
        print(df_out.to_json(orient="records", force_ascii=False, indent=2))
    else:
        print(df_out.to_string(index=False))


if __name__ == "__main__":
    main()
