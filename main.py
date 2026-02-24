#!/usr/bin/env python3
"""
命令行入口：不启动 API，直接运行一次图并打印结果。
用法: python main.py
或: OPENAI_API_KEY=xxx python main.py
"""
from datetime import date
from japanai.real_estate_graph import RealEstateGraph


def main():
    graph = RealEstateGraph(debug=False)
    property_of_interest = "东京都港区 某公寓，投资用"
    user_profile = "预算约 5000 万日元，投资用途，非居住者，计划长期持有"
    trade_date = str(date.today())

    final_state, signal = graph.propagate(
        property_of_interest=property_of_interest,
        user_profile=user_profile,
        trade_date=trade_date,
    )

    print("=== 最终信号 ===")
    print(signal)
    print("\n=== 风控裁判结论 ===")
    print(final_state.get("final_decision", ""))
    print("\n=== 投资计划 ===")
    print(final_state.get("investment_plan", "")[:500])
    print("\n=== 交易员计划 ===")
    print(final_state.get("trader_investment_plan", "")[:500])


if __name__ == "__main__":
    main()
