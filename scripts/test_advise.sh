#!/usr/bin/env bash
# 后端启动后测试「日本价格」相关建议（默认 MiniMax + Token 已写死后端）
# 用法: ./scripts/test_advise.sh  或  bash scripts/test_advise.sh

set -e
BASE="${1:-http://localhost:8000}"

echo ">>> Health check $BASE/health"
curl -s "$BASE/health" | head -1
echo ""

echo ">>> POST $BASE/advise (日本地产价格/投资建议)"
curl -s -X POST "$BASE/advise" \
  -H "Content-Type: application/json" \
  -d '{
    "property_of_interest": "东京都港区 某公寓，想了解当前日本地产价格与投资回报",
    "user_profile": "预算约 5000 万日元，投资用途，非居住者，计划长期持有，想查日本房价与租金回报"
  }' | python3 -m json.tool
