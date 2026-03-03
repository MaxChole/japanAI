#!/usr/bin/env bash
# 后端启动后测试「日本价格」相关建议（默认 MiniMax + Token 已写死后端）
# 使用现实中存在的东京公寓地址与户籍。用法: ./scripts/test_advise.sh [BASE_URL]

set -e
BASE="${1:-http://localhost:8000}"

echo ">>> Health check $BASE/health"
curl -s "$BASE/health" | head -1
echo ""

echo ">>> POST $BASE/advise (少开分析师 + 仅风控裁判一人评判)"
curl -s -X POST "$BASE/advise" \
  -H "Content-Type: application/json" \
  -d '{
    "property_of_interest": "東京都港区浜松町2丁目 パークコート浜離宮ザタワー、2LDK 约84㎡、23层、2019年建成，JR浜松町站约550m。想了解日本地产价格与投资回报",
    "user_profile": "预算约1.5亿日元，投资用途，非居住者，计划长期持有",
    "household_region": "中国",
    "selected_analysts": ["location", "legal", "yield"],
    "use_risk_debate": false
  }' | python3 -m json.tool
