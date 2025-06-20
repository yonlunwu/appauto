from uuid import uuid4
from typing import List
from ...base_component import BaseComponent
from .models.model import Model
from .models.model_store import ModelStore
from .models.model_instance import ModelInstance
from .scene import Chat
from .api_key import APIKey
from .dashboard import DashBoard
from .users import AMaaSUser
from ....config_manager.config_logging import LoggingConfig
from ....utils_manager.custom_list import CustomList

logger = LoggingConfig.get_logger()


class AMaaS(BaseComponent):
    OBJECT_TOKEN = None

    @property
    def model_stores(self) -> CustomList[ModelStore]:
        params = dict(page=1, perPage=100)
        res = self.get("list_model_stores", params, ModelStore.GET_URL_MAP)
        return CustomList(
            [
                ModelStore(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
                for item in res.data.get("items")
            ]
        )

    @property
    def init_model_stores(self):
        """模型管理 - 模型中心"""
        return self.model_stores.filter(source="init")

    @property
    def upload_model_stores(self):
        """模型管理 - 模型中心"""
        return self.model_stores.filter(source="upload")

    @property
    def llm_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="llm")

    @property
    def vlm_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="vlm")

    @property
    def embedding_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="embedding")

    @property
    def rerank_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="rerank")

    @property
    def parser_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="parser")

    @property
    def audio_model_stores(self) -> List[ModelStore]:
        return self.model_stores.filter(type="audio")

    @property
    def models(self) -> List[Model]:
        res = self.get(alias="get_models", url_map=Model.GET_URL_MAP)
        return [
            Model(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip) for item in res.data.get("items")
        ]

    @property
    def llm_chats(self):
        """试验场景-对话"""
        res = self.get(alias="get_models", url_map=Chat.GET_URL_MAP, params=dict(categories="llm"))
        logger.debug(res)
        return [Chat(self.mgt_ip, self.port, object_id=item.id, data=item) for item in res.data]

    @property
    def model_instances(self) -> List[ModelInstance]:
        res = self.get(alias="get_instances", url_map=ModelInstance.GET_URL_MAP)
        return [
            ModelInstance(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
            for item in res.data.get("items")
        ]

    @property
    def api_keys(self):
        params = dict(page=1, perpage=1000)
        res = self.get("list_all", url_map=APIKey.GET_URL_MAP, params=params)
        return [APIKey(self.mgt_ip, self.port, object_id=item.id, data=item) for item in res.data.get("items")]

    def create_api_key(self, name: str = None, expires_in=None, timeout: int = None):
        # TODO 时间戳有点诡异，是个 1970 年的时间戳？
        data = {"expires_in": expires_in or "30761967", "name": name or str(uuid4())}
        res = self.post("create", url_map=APIKey.POST_URL_MAP, json=data, timeout=timeout)
        return APIKey(self.mgt_ip, self.port, object_id=res.data.id, data=res.data)

    @property
    def users(self):
        params = dict(page=1, perpage=1000)
        res = self.get("list_all", url_map=AMaaSUser.GET_URL_MAP, params=params)
        return [AMaaSUser(self.mgt_ip, self.port, object_id=item.id, data=item) for item in res.data.get("items")]

    def create_user(self, username, passwd, is_admin: bool, desc: str = None, timeout: int = None):
        data = {
            "username": username,
            "password": passwd,
            "is_admin": is_admin,
            "full_name": desc,
            "require_password_change": False,
        }
        res = self.post("create", url_map=AMaaSUser.POST_URL_MAP, json=data, timeout=timeout)
        return AMaaSUser(self.mgt_ip, self.port, object_id=res.data.id, data=res.data)

    @property
    def dashboard(self):
        res = self.get("get", url_map=DashBoard.GET_URL_MAP)
        return DashBoard(self.mgt_ip, self.port, data=res.data)
