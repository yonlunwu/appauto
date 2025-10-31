import addict
from typing import TYPE_CHECKING
from functools import cached_property
from ....connection_manager.http import HttpClient

from ....config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

if TYPE_CHECKING:
    from . import AMaaS


class BaseComponent(object):
    OBJECT_TOKEN = None
    ACCESS_TOKEN = None

    GET_URL_MAP = {}
    PUT_URL_MAP = {}
    POST_URL_MAP = {}
    DELETE_URL_MAP = {}

    REFRESH_ALIAS = "get_self"

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
        amaas: "AMaaS" = None,
    ):
        self.mgt_ip = mgt_ip
        self.port = port
        self.object_id = object_id
        self.user = username
        self.passwd = passwd
        self.data = data
        self.ssl_enabled = ssl_enabled
        self.parent_tokens = parent_tokens or {}
        self.amaas = amaas

    def refresh(self, alias=None):
        res = self.get(alias or self.REFRESH_ALIAS)

        if not alias:
            self.data = res.data

        return res

    def refresh_token(self):
        del self.__dict__["http"]
        del self.__dict__["headers"]
        del self.__dict__["token"]

        self.login(refresh=True)

    @cached_property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Cookie": f"AMES_session={self.token}",
        }

    def login(self, refresh=False):
        if refresh:
            BaseComponent.ACCESS_TOKEN = None

        if BaseComponent.ACCESS_TOKEN is None:
            data = {"username": self.user, "password": self.passwd}
            res = HttpClient().post(f"{self.url_prefix}/api/auth/login", data=data)
            BaseComponent.ACCESS_TOKEN = res.data.access_token

        return BaseComponent.ACCESS_TOKEN

    def request_callback(self, response):
        retry = True
        try:
            if response.status_code == 401:
                self.refresh_token()
            elif response.status_code == 200 and response.json().get("ec", "EOK") == "EOK":
                retry = False
        finally:
            return addict.Dict(retry=retry, token=self.token)

    @cached_property
    def token(self):
        return self.login()

    @cached_property
    def http(self):
        return HttpClient(headers=self.headers)

    @cached_property
    def http_with_file(self):
        return HttpClient(headers={"Authorization": f"Bearer {self.token}", "Cookie": f"AMES_session={self.token}"})

    # 测试 sglang 不需要带前端
    @cached_property
    def http_without_token(self):
        return HttpClient(headers={"accept": "application/json", "Content-Type": "application/json"})

    @cached_property
    def url_prefix(self):
        return f"{'https' if self.ssl_enabled else 'http'}://{self.mgt_ip}:{self.port}"

    def full_url(self, url_map, alias):
        url = url_map[alias]
        return f"{self.url_prefix}/api{url.format(**self.object_tokens)}"

    @property
    def current_object_token(self):
        return {self.OBJECT_TOKEN: self.object_id}

    @property
    def object_tokens(self):
        if self.OBJECT_TOKEN and self.object_id:
            return dict(**self.parent_tokens, **self.current_object_token)

        return self.parent_tokens

    def get(self, alias, params=None, url_map=None, timeout=None, headers=None, encode_result=True, **kwargs):
        url_map = url_map or self.GET_URL_MAP
        # TODO 完善 self.object_tokens
        return self.http.get(
            self.full_url(url_map, alias),
            params,
            headers,
            encode_result,
            timeout,
            **kwargs,
        )

    def post(
        self,
        alias,
        params=None,
        data=None,
        json_data=None,
        url_map=None,
        timeout=None,
        headers=None,
        encode_result=True,
        stream=False,
        **kwargs,
    ):
        """
        encode_result 只在 stream=False 时才生效;
        """
        url_map = url_map or self.POST_URL_MAP
        url = self.full_url(url_map, alias)
        # 合并 headers：优先使用外部传入的 headers，否则使用默认 headers
        hdrs = dict(self.headers) if headers is None else dict(headers)

        if not stream:
            if kwargs.get("files"):
                hdrs.pop("Content-Type", None)
            return self.http_with_file.post(url, params, data, json_data, hdrs, encode_result, timeout, **kwargs)

        return self.http.stream_request("POST", url, params, data, json_data, hdrs, timeout, **kwargs)

    # 测试 sglang 不需要带前端
    def post_without_token(
        self,
        alias,
        params=None,
        data=None,
        json_data=None,
        url_map=None,
        timeout=None,
        headers=None,
        encode_result=True,
        stream=False,
        **kwargs,
    ):
        url_map = url_map or self.POST_URL_MAP
        url = url_map[alias]
        url = f"{self.url_prefix}/{url.format(**self.object_tokens)}"
        if not stream:
            return self.http_without_token.post(url, params, data, json_data, headers, encode_result, timeout, **kwargs)

        return self.http_without_token.stream_request(
            "POST", url, params, data, json_data=json_data, headers=headers, timeout=timeout, **kwargs
        )

    def delete(
        self,
        alias,
        params=None,
        data=None,
        json_data=None,
        url_map=None,
        timeout=None,
        headers=None,
        encode_result=True,
        **kwargs,
    ):
        url_map = url_map or self.DELETE_URL_MAP
        # TODO 完善 self.object_tokens
        return self.http.delete(
            self.full_url(url_map, alias),
            params,
            data,
            json_data=json_data,
            headers=headers,
            encode_result=encode_result,
            timeout=timeout,
            **kwargs,
        )
