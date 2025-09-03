from .llm import LLMModelStore
from .vlm import VLMModelStore
from .embedding import EmbeddingModelStore
from .rerank import RerankModelStore
from .parser import ParserModelStore
from .audio import AudioModelStore

from .base import BaseModelStore
from appauto.manager.utils_manager.custom_list import CustomList


class ModelStore(BaseModelStore):

    def refresh(self):
        params = dict(page=1, perPage=100, source="init")
        res = self.get("get_self", params)
        self.data = res.data.get("items")
        return res

    @property
    def llm(self) -> CustomList[LLMModelStore]:
        return CustomList(
            [
                LLMModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "llm"
            ]
        )

    @property
    def vlm(self) -> CustomList[VLMModelStore]:
        return CustomList(
            [
                VLMModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "vlm"
            ]
        )

    @property
    def embedding(self) -> CustomList[EmbeddingModelStore]:
        return CustomList(
            [
                EmbeddingModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "embedding"
            ]
        )

    @property
    def rerank(self) -> CustomList[RerankModelStore]:
        return CustomList(
            [
                RerankModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "rerank"
            ]
        )

    @property
    def parser(self) -> CustomList[ParserModelStore]:
        return CustomList(
            [
                ParserModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "parser"
            ]
        )

    @property
    def audio(self) -> CustomList[AudioModelStore]:
        return CustomList(
            [
                AudioModelStore(self.mgt_ip, self.port, object_id=item.id, data=item)
                for item in self.data
                if item["type"] == "audio"
            ]
        )
