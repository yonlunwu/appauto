import addict
from typing import Literal
from functools import cached_property
from ..connection_manager.http import HttpClient

from ..config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class BaseComponent(object):
    OBJECT_TOKEN = None
    GET_URL_MAP = {}
    PUT_URL_MAP = {}
    POST_URL_MAP = {}
    DELETE_URL_MAP = {}

    def __init__(
        self,
        mgt_ip=None,
        port=None,
        username="admin",
        passwd="123456",
        object_id=None,
        data=None,
        ssl_enabled=False,
        parent_tokens=None,
    ):
        self.mgt_ip = mgt_ip
        self.port = port
        self.object_id = object_id
        self.user = username
        self.passwd = passwd
        self.data = data
        self.ssl_enabled = ssl_enabled
        self.parent_tokens = parent_tokens or {}

    @cached_property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Cookie": f"AMES_session={self.token}",
        }

    def login(self):
        data = {"username": self.user, "password": self.passwd}
        return HttpClient().post(f"{self.url_prefix}/api/auth/login", data=data)

    def request_callback(self, response):
        retry = True
        try:
            if response.status_code == 401:
                self.login(force=True)
            elif response.status_code == 200 and response.json().get("ec", "EOK") == "EOK":
                retry = False
        finally:
            return addict.Dict(retry=retry, token=self.token)

    @cached_property
    def token(self):
        return self.login().data.access_token

    @cached_property
    def http(self):
        return HttpClient(headers=self.headers)

    @cached_property
    def url_prefix(self):
        return f"{'https' if self.ssl_enabled else 'http'}://{self.mgt_ip}:{self.port}"

    # TODO 从 map 中获取 url & 拼接前缀
    def get(self, url: str, **kwargs):
        return self.http.get(url, **kwargs)

    # TODO 这只是个 demo
    def get_model_center(self):
        """点击模型中心页面"""
        return self.http.get(f"{self.url_prefix}/api/v1/kllm/models/types")

    def list_models(
        self,
        pagenum: int = None,
        per_page: int = None,
        source=None,
        type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"] = None,
    ):
        """进入模型中心页面，查看不同类型的 models"""
        params = {}
        if pagenum:
            params["page"] = pagenum
        if per_page:
            params["perPage"] = per_page
        if source:
            params["source"] = source
        if type_:
            params["type"] = type_

        return self.http.get(f"{self.url_prefix}/api/v1/kllm/model-store", params=params)

    @cached_property
    def get_model_types(self) -> Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]:
        return self.get_model_center().data.types

    @property
    def current_object_token(self):
        return {self.OBJECT_TOKEN: self.object_id}

    @property
    def object_tokens(self):
        if self.OBJECT_TOKEN and self.object_id:
            return dict(**self.parent_tokens, **self.current_object_token)

        return self.parent_tokens

    def raw_get(self, alias, params=None, url_map=None, timeout=None, headers=None, encode_result=True, **kwargs):
        url_map = url_map or self.GET_URL_MAP
        url = url_map[alias]
        # TODO 完善 self.object_tokens
        return self.http.get(
            f"{self.url_prefix}/api{url.format(**self.object_tokens)}",
            params,
            headers,
            encode_result,
            timeout,
            **kwargs,
        )

    def raw_post(
        self,
        alias,
        params=None,
        data=None,
        json=None,
        url_map=None,
        timeout=None,
        headers=None,
        encode_result=True,
        **kwargs,
    ):
        url_map = url_map or self.POST_URL_MAP
        url = url_map[alias]
        # TODO 完善 self.object_tokens
        return self.http.post(
            f"{self.url_prefix}/api{url.format(**self.object_tokens)}",
            params,
            data,
            json=json,
            headers=headers,
            encode_result=encode_result,
            timeout=timeout,
            **kwargs,
        )

    def raw_delete(
        self,
        alias,
        params=None,
        data=None,
        json=None,
        url_map=None,
        timeout=None,
        headers=None,
        encode_result=True,
        **kwargs,
    ):
        url_map = url_map or self.DELETE_URL_MAP
        url = url_map[alias]
        # TODO 完善 self.object_tokens
        return self.http.delete(
            f"{self.url_prefix}/api{url.format(**self.object_tokens)}",
            params,
            data,
            json=json,
            headers=headers,
            encode_result=encode_result,
            timeout=timeout,
            **kwargs,
        )
