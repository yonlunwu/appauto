from uuid import uuid4
from typing import List, Optional
from .base_component import BaseComponent
from .models import Worker, ModelStore, Model
from .scene import Scene
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
    def init_model_store(self) -> ModelStore:
        """模型管理 - 模型中心"""
        params = dict(page=1, perPage=100, source="init")
        res = self.get("get_self", params, ModelStore.GET_URL_MAP)
        return ModelStore(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def upload_model_store(self) -> ModelStore:
        """模型管理 - 私有模型"""
        params = dict(page=1, perPage=100, source="upload")
        res = self.get("get_self", params, ModelStore.GET_URL_MAP)
        return ModelStore(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def model(self) -> Model:
        """模型管理-模型运行"""
        res = self.get("get_self", url_map=Model.GET_URL_MAP)
        return Model(self.mgt_ip, self.port, data=res.data.get("items"), amaas=self)

    @property
    def scene(self) -> Scene:
        """试验场景"""
        return Scene(self.mgt_ip, self.port, amaas=self)

    @property
    def workers(self) -> Optional[CustomList[Worker]]:
        """模型管理-模型加速"""
        res = self.get(alias="get_self", url_map=Worker.GET_URL_MAP)
        if res.retcode == 0:
            return CustomList(
                [
                    Worker(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip, amaas=self)
                    for item in res.data.worker_resource_list
                ]
            )

    @property
    def api_keys(self) -> CustomList[APIKey]:
        """API 密钥"""
        params = dict(page=1, perpage=1000)
        res = self.get("get_self", url_map=APIKey.GET_URL_MAP, params=params)
        return CustomList(
            [APIKey(self.mgt_ip, self.port, object_id=item.id, data=item, amaas=self) for item in res.data.get("items")]
        )

    def create_api_key(self, name: str = None, expires_in=None, timeout: int = None):
        # TODO 时间戳有点诡异，是个 1970 年的时间戳？
        data = {"expires_in": expires_in or "30761967", "name": name or str(uuid4())}
        res = self.post("create", url_map=APIKey.POST_URL_MAP, json_data=data, timeout=timeout)
        return APIKey(self.mgt_ip, self.port, object_id=res.data.id, data=res.data, amaas=self)

    @property
    def users(self) -> List[AMaaSUser]:
        """用户管理"""
        params = dict(page=1, perpage=1000)
        res = self.get("get_self", url_map=AMaaSUser.GET_URL_MAP, params=params)
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
    def dashboard(self) -> DashBoard:
        """数据概览"""
        res = self.get("get_self", url_map=DashBoard.GET_URL_MAP)
        return DashBoard(self.mgt_ip, self.port, data=res.data, amaas=self)
