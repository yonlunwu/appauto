from .llm import LLMModel
from .vlm import VLMModel
from .embedding import EmbeddingModel
from .rerank import RerankModel
from .parser import ParserModel
from .audio import AudioModel

from .base import BaseModel

from appauto.manager.utils_manager.custom_list import CustomList


# TODO 要继承 BaseComponent
class Model(BaseModel):

    def refresh(self, alias=None):
        res = super().refresh(alias)
        self.data = res.data.get("items")
        return res

    @property
    def llm(self) -> CustomList[LLMModel]:
        return CustomList(
            [
                LLMModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["llm"]
            ]
        )

    @property
    def vlm(self) -> CustomList[VLMModel]:
        return CustomList(
            [
                VLMModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["vlm"]
            ]
        )

    @property
    def embedding(self) -> CustomList[EmbeddingModel]:
        return CustomList(
            [
                EmbeddingModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["embedding"]
            ]
        )

    @property
    def rerank(self) -> CustomList[RerankModel]:
        return CustomList(
            [
                RerankModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["rerank"]
            ]
        )

    @property
    def parser(self) -> CustomList[ParserModel]:
        return CustomList(
            [
                ParserModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["parser"]
            ]
        )

    @property
    def audio(self):
        return CustomList(
            [
                AudioModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self.amaas)
                for item in self.data
                if item["categories"] == ["speech_to_text"]
            ]
        )
