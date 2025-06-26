import json
import httpx
import addict
from appauto.manager.config_manager import LoggingConfig
from typing import Optional, Dict, Any, Union
from functools import cached_property

logger = LoggingConfig.get_logger()


class HttpClient:
    def __init__(
        self,
        headers: Optional[Dict[str, str]] = None,
        verify: bool = False,
    ):
        self.headers = headers or {}
        self.verify = verify
        self._client = None

    @cached_property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(headers=self.headers, verify=self.verify)
            logger.info(self._client.headers)
        return self._client

    def token(self):
        # TODO 获取 token
        ...

    def _log_request(self, method: str, url: str, **kwargs):
        logger.info(f"[Request] {method.upper()} {url}")
        for key in ["params", "json", "data"]:
            if kwargs.get(key):
                logger.info(f"[Request] {key.capitalize()}: {kwargs[key]}")

    def _log_response(self, response: httpx.Response):
        logger.info(f"[Response] [{response.status_code}] {response.url}")
        try:
            logger.info(f"[Response] Body: {response.json()}")
        except Exception as e:
            logger.error(f"[Response] Body (text): {response.text} with Exception: {e}")

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        encode_result=True,
        timeout=None,
        **kwargs,
    ) -> Union[addict.Dict, httpx.Response]:
        self._log_request(method, url, params=params, data=data, json=json)

        try:
            response = self.client.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
            self._log_response(response)
            # TODO 除了 verify_rc 是否需要 verify_msg
            response.raise_for_status()

            return self.encode_result(response.text) if encode_result else response
        except httpx.HTTPError as e:
            logger.error(f"HTTP {method.upper()} {url} failed: {e}")
            raise

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        encode_result=True,
        timeout=None,
        **kwargs,
    ) -> Union[addict.Dict, httpx.Response]:
        # TODO params 是否需要转成 dict
        return self.request("GET", url, params, timeout=timeout, headers=headers, encode_result=encode_result, **kwargs)

    def post(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        encode_result=True,
        timeout=None,
        **kwargs,
    ) -> Union[addict.Dict, httpx.Response]:
        return self.request("POST", url, params, data, json, headers, encode_result, timeout, **kwargs)

    def put(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        encode_result=True,
        timeout=None,
        **kwargs,
    ) -> Union[addict.Dict, httpx.Response]:
        return self.request("PUT", url, params, data, json, headers, encode_result, timeout, **kwargs)

    def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        encode_result=True,
        timeout=None,
        **kwargs,
    ) -> Union[addict.Dict, httpx.Response]:
        return self.request("DELETE", url, params, data, json, headers, encode_result, timeout, **kwargs)

    def update_headers(self, headers: Dict[str, str]):
        """
        更新请求头，比如更新 token
        """
        self.headers.update(headers)
        if self._client:
            self._client.headers.update(headers)

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def encode_result(self, text):
        try:
            json_data = json.loads(text)
            return addict.Dict(json_data) if isinstance(json_data, dict) else json_data
        except Exception as e:
            logger.warning(f"error occurred while encoding result: {e}")
            return text

    def validate_return_msg(self, text):
        """成功后返回 {retcode: 0, retmsfg: success, data: {}}"""
        res = self.encode_result(text)
        assert res.retcode == 0
        assert res.retmsg == "success"

    def stream_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        """返回生成器上下文管理器"""
        self._log_request(method, url, params=params, data=data, json=json)

        try:
            # 直接返回生成器上下文管理器
            return self.client.stream(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
        except httpx.HTTPError as e:
            logger.error(f"Stream request failed: {e}")
            raise

    def process_stream(self, response):
        """获取 stream chunks 的文本内容"""
        full_content = ""
        for line in response.iter_lines():
            if not line or not line.startswith("data:"):
                continue
            payload = line.removeprefix("data:").strip()

            if payload == "[DONE]":
                break

            try:
                data = json.loads(payload)
                logger.info(f"per stream link payload: {data}")
                chunk = data["choices"][0]["delta"].get("content")
                if chunk:
                    full_content += chunk
                    # 实时输出
                    logger.debug(chunk)
                    logger.debug(full_content)

            except Exception as e:
                logger.error(f"Process stream request failed: {e}, init_payload: {payload}")
                raise

        logger.info(f"full_content: {full_content}")
        return full_content
