from typing import Literal
from ....base_component import BaseComponent


class Chat(BaseComponent):
    OBJECT_TOKEN = "chat_id"

    GET_URL_MAP = dict(get_models="/v1/models")

    POST_URL_MAP = dict(
        chat="/v1/chat/completions",  # 对话
        # completions = "/v1/completions" #
    )

    def talk(
        self,
        content: str,
        model: str = None,
        stream=True,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        timeout=None,
        process_stream=False,
        encode_result=False,
    ):
        """
        model: 模型名称, 不指定则为自己;
        process_stream: 获取原始 stream or 对应的文本内容
        encode_result: 当指定 stream=False 时, 可以设置 encode_result=True, 此时可以获取文本.
        """
        data = {
            "messages": [{"content": content, "role": "user"}],
            "model": model or self.object_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        process_stream = process_stream if stream else False
        encode_result = False if stream else encode_result

        if stream:
            with self.post("chat", stream=stream, json_data=data, timeout=timeout) as res:
                return self.http.process_stream_amaas(res) if process_stream else res

        return self.post("chat", json_data=data, timeout=timeout, stream=stream, encode_result=encode_result)

    @property
    def display_model_name(self):
        return self.data.display_model_name

    @property
    def object(self) -> Literal["model"]:
        return self.data.object

    @property
    def owned_by(self) -> Literal["AMES"]:
        return self.data.owned_by

    @property
    def meta(self) -> Literal[None]:
        return self.data.meta
