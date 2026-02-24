"""
Mock 数据源：在无真实 API 时返回静态/规则数据，供分析师工具调用。
后续可替换为国土交通省地价、税率 API、租金数据等。
"""

# ---------- 区域/地段 ----------
def get_location_data(region: str, purpose: str) -> str:
    """
    返回区域相关结构化信息（mock）。
    region: 如 "东京都港区", "大阪市北区"
    purpose: "自住" | "投资"
    """
    return f"""# 区域数据（Mock）- {region}
- 用途假设: {purpose}
- 地价趋势: 近年平稳微涨（mock）
- 交通: 主要线路 5–10 分钟（mock）
- 人口: 区内人口稳定（mock）
- 风险点: 需结合具体楼盘与实地考察
- 数据来源: 当前为模拟数据，正式环境可接入国土交通省地价等
"""


# ---------- 法律/合规 ----------
def get_legal_faq(is_non_resident: bool, purpose: str) -> str:
    """
    返回与外国人购房、产权、租赁法规相关的要点（mock）。
    """
    resident_note = "非居住者" if is_non_resident else "居住者"
    return f"""# 法律/合规要点（Mock）- {resident_note}、{purpose}
- 外国人购房: 日本原则上无限制，但贷款可能受限（非居住者难贷）
- 产权: 所有权与借地权需区分；产权登记需确认
- 租赁法规: 借家法保护租户，解约与涨租有法定限制
- 管理规约: 需确认修缮金、宠物、转租等条款
- 数据来源: 当前为模拟摘要，具体以律师意见为准
"""


# ---------- 税务 ----------
def get_tax_rules(purpose: str, holding_years: str) -> str:
    """
    返回固定资产税、所得税、源泉税、折旧等规则摘要（mock）。
    holding_years: 如 "5年", "长期"
    """
    return f"""# 税务规则摘要（Mock）- {purpose}、持有期 {holding_years}
- 固定资产税·都市计划税: 按评估额约 1.4%+（mock）
- 所得税: 租金收入计入综合课税；投资用可折旧（木造 22 年、RC 等 47 年）
- 非居住者: 租金等源泉 20.42%；出售时源泉 10.21%（mock）
- 继承税·赠与税: 高额资产需注意申报与规划
- 数据来源: 当前为模拟，具体以税务师意见为准
"""


# ---------- 收益/现金流 ----------
def get_yield_inputs(
    rent_monthly: float,
    price: float,
    management_fee_ratio: float = 0.05,
    vacancy_ratio: float = 0.05,
) -> str:
    """
    根据用户输入的租金、售价、管理费比例、空置率等返回结构化数据（mock）。
    """
    gross_yield = (rent_monthly * 12) / price * 100 if price else 0
    net_rent = rent_monthly * (1 - management_fee_ratio) * (1 - vacancy_ratio)
    net_yield = (net_rent * 12) / price * 100 if price else 0
    return f"""# 收益数据（Mock）
- 月租金: {rent_monthly} 日元
- 售价: {price} 日元
- 表面回报率: {gross_yield:.2f}%
- 管理费比例: {management_fee_ratio*100:.0f}%
- 空置率假设: {vacancy_ratio*100:.0f}%
- 粗算净回报率: {net_yield:.2f}%
- 数据来源: 用户输入 + 模拟计算
"""
