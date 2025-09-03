from typing import List, Union
from .base import BaseScene


class Rerank(BaseScene):

    def talk(
        self,
        query: str = "叶文洁是谁",
        documents: Union[str, List[str]] = [
            "叶文洁是刘慈欣科幻小说《三体》中的关键人物，天体物理学家，曾是红岸基地技术人员，后成为地球三体组织统帅",
            "大模型技术是基于海量参数和复杂架构的深度学习模型，具有强大的数据处理和泛化能力，应用于自然语言处理、图像识别、语音合成等领域。",
            "罗辑是《三体》系列中重要角色，社会学教授，面壁者，执剑人，提出黑暗森林法则，守护人类文明。",
        ],
        top_n: int = 3,
        model: str = None,
        timeout=None,
    ):
        data = {
            "documents": documents if isinstance(documents, list) else [documents],
            "model": model or self.object_id,
            "top_n": top_n,
            "query": query,
        }

        return self.post("rerank", json_data=data, timeout=timeout, encode_result=True)
