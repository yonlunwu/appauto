"""
kllm 作为一个大的对象, 类比 tower, 下面包含多个子对象
    - 数据概览
    - 模型管理, 类比 block:iscsi_target
    - 试验场景
    - API 密钥
    - 用户管理
"""

from functools import cached_property
from typing import List
from ...base_component import BaseComponent
from .models.model import Model
from .models.model_store import ModelStore
from .models.model_instance import ModelInstance
from ....config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class Kllm(BaseComponent):
    OBJECT_TOKEN = None

    @property
    def model_stores(self) -> List[ModelStore]:
        """进入模型中心页面，查看不同类型的 models"""
        res = self.raw_get(alias="list_model_stores", url_map=ModelStore.GET_URL_MAP)
        return [
            ModelStore(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
            for item in res.data.get("items")
        ]

    @property
    def models(self) -> List[Model]:
        res = self.raw_get(alias="get_models", url_map=Model.GET_URL_MAP)
        return [
            Model(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip) for item in res.data.get("items")
        ]

    @property
    def model_instances(self) -> List[ModelInstance]:
        "http://117.133.60.227:5175/api/v1/kllm/models/3/instances?id=3&page=1&perPage=100"
        "http://117.133.60.227:5175/api/v1/kllm/model-instances"
        res = self.raw_get(alias="get_instances", url_map=ModelInstance.GET_URL_MAP)
        return [
            ModelInstance(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
            for item in res.data.get("items")
        ]
