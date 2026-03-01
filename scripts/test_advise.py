#!/usr/bin/env python3
"""
后端启动后，用 Python 请求 POST /advise，查询「日本价格」相关建议。
默认使用后端已配置的 MiniMax Token 与模型，无需传 llm_config。
用法: python3 scripts/test_advise.py [BASE_URL]
"""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
URL = f"{BASE.rstrip('/')}/advise"

payload = {
    "property_of_interest": "东京都港区 某公寓，想了解当前日本地产价格与投资回报",
    "user_profile": "预算约 5000 万日元，投资用途，非居住者，计划长期持有，想查日本房价与租金回报",
}

req = urllib.request.Request(
    URL,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read().decode())
    print("signal:", out.get("signal"))
    print("final_decision (前 500 字):", (out.get("final_decision") or "")[:500])
    print("location_report (前 300 字):", (out.get("location_report") or "")[:300])
except Exception as e:
    print("请求失败:", e)
    sys.exit(1)
