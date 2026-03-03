#!/usr/bin/env python3
"""
后端启动后，用 Python 请求 POST /advise，查询「日本价格」相关建议。
使用现实中存在的东京公寓地址与户籍信息，默认使用后端已配置的 MiniMax。
用法: python3 scripts/test_advise.py [BASE_URL]
"""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
URL = f"{BASE.rstrip('/')}/advise"

# 现实中存在的东京公寓：東京都港区浜松町 パークコート浜離宮ザタワー（Park Court 滨离宫塔）
# 少开分析师、仅风控裁判一人评判；含 policy 才能看到政策/规划报告（policy_report）
payload = {
    "property_of_interest": "東京都港区浜松町2丁目 パークコート浜離宮ザタワー（Park Court 滨离宫塔）、2LDK 约 84㎡、23 层、2019 年建成，邻近 JR 山手线浜松町站徒步约 550m、都营大江户线大门站约 450m。想了解当前日本地产价格与投资回报。",
    "user_profile": "预算约 1.5 亿日元，投资用途，非居住者，计划长期持有，想查日本房价与租金回报",
    "household_region": "中国",
    "selected_analysts": ["location", "legal", "policy", "yield"],
    "use_risk_debate": False,
}

req = urllib.request.Request(
    URL,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.loads(resp.read().decode())
    print("signal:", out.get("signal"))
    print("final_decision (前 500 字):", (out.get("final_decision") or "")[:500])
    print("location_report (前 300 字):", (out.get("location_report") or "")[:300])
    print("policy_report (前 300 字):", (out.get("policy_report") or "")[:300])
except Exception as e:
    print("请求失败:", e)
    sys.exit(1)
