from uuid import uuid4
from typing import List, Optional
from ...base_component import BaseComponent
from .models import Worker, ModelStore, Model
from .scene import Chat, Embedding, Rerank, MultiModel  # TODO 结构很像，可以 base_component
from .api_key import APIKey
from .dashboard import DashBoard
from .users import AMaaSUser
from ....config_manager.config_logging import LoggingConfig
from ....utils_manager.custom_list import CustomList

logger = LoggingConfig.get_logger()


class AMaaS(BaseComponent):
    OBJECT_TOKEN = None

    def __str__(self):
        return self.mgt_ip

    @property
    def model_stores(self) -> CustomList[ModelStore]:
        params = dict(page=1, perPage=100)
        res = self.get("list_model_stores", params, ModelStore.GET_URL_MAP)
        return CustomList(
            [
                ModelStore(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip, amaas=self)
                for item in res.data.get("items")
            ]
        )

    @property
    def init_model_stores(self) -> List[ModelStore]:
        """模型管理 - 模型中心"""
        return self.model_stores.filter(source="init")

    @property
    def upload_model_stores(self) -> List[ModelStore]:
        """模型管理 - 私有模型"""
        return self.model_stores.filter(source="upload")

    @property
    def llm_model_stores(self) -> List[ModelStore]:
        """模型中心-llm"""
        return self.model_stores.filter(type="llm")

    @property
    def vlm_model_stores(self) -> List[ModelStore]:
        """模型中心-vlm"""
        return self.model_stores.filter(type="vlm")

    @property
    def embedding_model_stores(self) -> List[ModelStore]:
        """模型中心-embedding"""
        return self.model_stores.filter(type="embedding")

    @property
    def rerank_model_stores(self) -> List[ModelStore]:
        """模型中心-rerank"""
        return self.model_stores.filter(type="rerank")

    @property
    def parser_model_stores(self) -> List[ModelStore]:
        """模型中心-parser"""
        return self.model_stores.filter(type="parser")

    @property
    def audio_model_stores(self) -> List[ModelStore]:
        """模型中心-audio"""
        return self.model_stores.filter(type="audio")

    @property
    def models(self) -> CustomList[Model]:
        """模型管理-模型运行"""
        res = self.get(alias="get_models", url_map=Model.GET_URL_MAP)
        return CustomList(
            [
                Model(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip, amaas=self)
                for item in res.data.get("items")
            ]
        )

    @property
    def workers(self) -> Optional[CustomList[Worker]]:
        """模型管理-模型加速"""
        res = self.get(alias="get_resource_list", url_map=Worker.GET_URL_MAP)
        # TODO 当前 amaas 如果成功返回 retcode 是 0
        #  {'retcode': 0, 'retmsg': 'success', 'data': 'xxx'}
        if res.retcode == 0:
            return CustomList(
                [
                    Worker(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip, amaas=self)
                    for item in res.data.worker_resource_list
                ]
            )

    @property
    def llm_chats(self) -> CustomList[Chat]:
        """试验场景-对话"""
        res = self.get(alias="get_models", url_map=Chat.GET_URL_MAP, params=dict(categories="llm"))
        logger.debug(res)
        return CustomList([Chat(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data])

    @property
    def embedding_chats(self) -> CustomList[Embedding]:
        """试验场景-embedding"""
        res = self.get(alias="get_models", url_map=Chat.GET_URL_MAP, params=dict(categories="embedding"))
        logger.debug(res)
        return CustomList(
            [Embedding(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data]
        )

    @property
    def rerank_chats(self) -> CustomList[Rerank]:
        """试验场景-rerank"""
        res = self.get(alias="get_models", url_map=Chat.GET_URL_MAP, params=dict(categories="rerank"))
        logger.debug(res)
        return CustomList(
            [Rerank(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data]
        )

    @property
    def multi_model_chats(self) -> CustomList[MultiModel]:
        """试验场景-rerank"""
        res = self.get(alias="get_models", url_map=Chat.GET_URL_MAP, params=dict(categories="vlm"))
        logger.debug(res)
        return CustomList(
            [MultiModel(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data]
        )

    @property
    def api_keys(self) -> CustomList[APIKey]:
        """API 密钥"""
        params = dict(page=1, perpage=1000)
        res = self.get("list_all", url_map=APIKey.GET_URL_MAP, params=params)
        return CustomList(
            [APIKey(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data.get("items")]
        )

    def create_api_key(self, name: str = None, expires_in=None, timeout: int = None):
        # TODO 时间戳有点诡异，是个 1970 年的时间戳？
        data = {"expires_in": expires_in or "30761967", "name": name or str(uuid4())}
        res = self.post("create", url_map=APIKey.POST_URL_MAP, json_data=data, timeout=timeout)
        return APIKey(self.mgt_ip, self.port, object_id=res.data.id, data=res.data, amaas=self)

    @property
    def users(self):
        """用户管理"""
        params = dict(page=1, perpage=1000)
        res = self.get("list_all", url_map=AMaaSUser.GET_URL_MAP, params=params)
        return [
            AMaaSUser(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self)
            for item in res.data.get("items")
        ]

    def create_user(self, username, passwd, is_admin: bool, desc: str = None, timeout: int = None):
        data = {
            "username": username,
            "password": passwd,
            "is_admin": is_admin,
            "full_name": desc,
            "require_password_change": False,
        }
        res = self.post("create", url_map=AMaaSUser.POST_URL_MAP, json_data=data, timeout=timeout)
        return AMaaSUser(self.mgt_ip, self.port, object_id=res.data.id, data=res.data, amaas=self)

    @property
    def dashboard(self):
        """数据概览"""
        res = self.get("get", url_map=DashBoard.GET_URL_MAP)
        return DashBoard(self.mgt_ip, self.port, data=res.data, amaas=self)
