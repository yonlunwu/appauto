from ...base_component import BaseComponent
from ....server_manager import SGLangServer


class SGLang(BaseComponent):
    OBJECT_TOKEN = "sglang_id"

    POST_URL_MAP = dict(chat="v1/chat/completions")

    def talk(
        self,
        content: str,
        model: str = None,  # TODO 不能是 None
        stream=True,
        max_tokens: int = None,
        temperature: int = None,  # TODO 非必须 int
        top_p: int = None,
        sys_promt_content=None,
        process_stream=False,
        timeout=None,
        encode_result=False,
    ):

        payload = {
            "messages": [{"role": "system", "content": sys_promt_content or ""}, {"role": "user", "content": content}],
            "model": model,
        }

        if stream:
            payload["stream"] = stream
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if temperature:
            payload["temperature"] = temperature
        if top_p:
            payload["top_p"] = top_p

        # 获取原始 stream
        if not process_stream:
            return self.post_without_token("chat", json=payload, timeout=timeout, encode_result=encode_result)

        with self.post_without_token("chat", json=payload, timeout=timeout, stream=stream) as response:
            return self.http_without_token.process_stream(response)

    def server(self) -> SGLangServer: ...
