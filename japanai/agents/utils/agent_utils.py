"""
Agent 通用工具：create_msg_delete 用于在分析师链中清空/占位 messages，
以控制上下文长度（兼容部分模型的 context 限制）。
"""
from langchain_core.messages import HumanMessage, RemoveMessage


def create_msg_delete():
    """
    返回一个节点函数：清空当前 messages 并加入占位 HumanMessage，
    避免空列表或过长历史导致的问题。
    """

    def delete_messages(state):
        removal_ops = [RemoveMessage(id=m.id) for m in state["messages"]]
        placeholder = HumanMessage(content="Continue")
        return {"messages": removal_ops + [placeholder]}

    return delete_messages
