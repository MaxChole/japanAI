"""
基于 BM25 的「情境-建议」记忆：用于检索与当前情境相似的历史情境及其建议，
供 Bull/Bear、Research Manager、Trader、Risk Manager 等节点参考，减少重复错误。
"""
import re
from typing import List, Tuple

from rank_bm25 import BM25Okapi


class RealEstateSituationMemory:
    """地产情境记忆：存储 (情境描述, 建议) 对，按 BM25 检索最相似的若干条。"""

    def __init__(self, name: str, config: dict = None):
        """
        Args:
            name: 记忆实例名称（如 bull_memory, risk_manager_memory）
            config: 配置字典（保留接口兼容，BM25 不使用）
        """
        self.name = name
        self.documents: List[str] = []
        self.recommendations: List[str] = []
        self.bm25 = None

    def _tokenize(self, text: str) -> List[str]:
        """简单分词：小写 + 按非字母数字切分，便于 BM25 索引。"""
        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens

    def _rebuild_index(self) -> None:
        """新增文档后重建 BM25 索引。"""
        if self.documents:
            tokenized_docs = [self._tokenize(doc) for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_docs)
        else:
            self.bm25 = None

    def add_situations(self, situations_and_advice: List[Tuple[str, str]]) -> None:
        """
        批量添加 (情境, 建议) 对；用于反思后写入历史经验。

        Args:
            situations_and_advice: [(situation_text, recommendation_text), ...]
        """
        for situation, recommendation in situations_and_advice:
            self.documents.append(situation)
            self.recommendations.append(recommendation)
        self._rebuild_index()

    def get_memories(
        self, current_situation: str, n_matches: int = 1
    ) -> List[dict]:
        """
        按 BM25 相似度检索与当前情境最接近的 n_matches 条建议。

        Args:
            current_situation: 当前情境文本（通常为多份 report 的拼接）
            n_matches: 返回条数

        Returns:
            [{"matched_situation": str, "recommendation": str, "similarity_score": float}, ...]
        """
        if not self.documents or self.bm25 is None:
            return []

        query_tokens = self._tokenize(current_situation)
        scores = self.bm25.get_scores(query_tokens)
        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:n_matches]

        results = []
        max_score = max(scores) if max(scores) > 0 else 1.0
        for idx in top_indices:
            normalized = scores[idx] / max_score if max_score > 0 else 0.0
            results.append(
                {
                    "matched_situation": self.documents[idx],
                    "recommendation": self.recommendations[idx],
                    "similarity_score": normalized,
                }
            )
        return results

    def clear(self) -> None:
        """清空所有记忆。"""
        self.documents = []
        self.recommendations = []
        self.bm25 = None
