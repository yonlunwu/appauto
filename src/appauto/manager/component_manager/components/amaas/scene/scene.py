from .base import BaseScene
from .llm import LLM
from .embedding import Embedding
from .vlm import VLM
from .rerank import Rerank


from appauto.manager.utils_manager.custom_list import CustomList


class Scene(BaseScene):

    @property
    def llm(self) -> CustomList[LLM]:
        res = self.get(alias="get_self", params=dict(categories="llm"))
        return CustomList([LLM(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data])

    @property
    def vlm(self) -> CustomList[VLM]:
        res = self.get(alias="get_self", params=dict(categories="vlm"))
        return CustomList([VLM(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data])

    @property
    def embedding(self) -> CustomList[Embedding]:
        res = self.get(alias="get_self", params=dict(categories="embedding"))
        return CustomList(
            [Embedding(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data]
        )

    @property
    def rerank(self) -> CustomList[Rerank]:
        res = self.get(alias="get_self", params=dict(categories="rerank"))
        return CustomList(
            [Rerank(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data]
        )
