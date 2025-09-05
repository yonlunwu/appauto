"""
模型管理 - 模型中心
"""

import abc
from functools import cached_property
from ...base_component import BaseComponent


class BaseModelStore(BaseComponent):
    OBJECT_TOKEN = "model_store_id"

    GET_URL_MAP = dict(
        get_self="/v1/kllm/model-store",
        aaa="/v1/kllm/model-store/importable",
        bbb="/v1/kllm/model-store/import",
        ccc="/v1/kllm/model-store/{model_store_id}",
    )

    PUT_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    POST_URL_MAP = dict(
        check="/v1/kllm/model-store/check",
        run="/v1/kllm/model-store/run",
        get_run_rule="/v1/kllm/model-store/get_run_rule",
    )

    DELETE_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    @abc.abstractmethod
    def check(self): ...

    @abc.abstractmethod
    def run(self): ...

    def get_run_rule(self, timeout=None):
        data = {"id": self.object_id}
        return self.post("get_run_rule", json_data=data, timeout=timeout)

    @cached_property
    def type(self):
        return self.data.type

    @cached_property
    def name(self):
        return self.data.name

    @property
    def source(self):
        return self.data.source

    @property
    def backend_type(self):
        return self.data.backend_type

    @property
    def local_path(self):
        return self.data.local_path

    @property
    def dir_path(self):
        return self.data.dir_path

    @property
    def weight_size(self):
        return self.data.weight_size

    @property
    def family(self):
        return self.data.family

    @property
    def quanted_type(self):
        return self.data.quanted_type

    @property
    def categories(self):
        return self.data.categories

    @property
    def required_vram(self):
        return self.data.required_vram

    @property
    def required_dram(self):
        return self.data.required_dram

    @property
    def required_disk(self):
        return self.data.required_disk

    @property
    def worker_name(self):
        return self.data.worker_name
