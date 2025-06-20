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
    ):
        """
        model: 模型名称, 不指定则为自己;
        process_stream: 获取原始 stream or 对应的文本内容
        """
        data = {
            "messages": [{"content": content, "role": "user"}],
            "model": model or self.object_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }
        # 获取原始 stream
        if not process_stream:
            return self.post("chat", json=data, timeout=timeout, encode_result=False)

        with self.post("chat", json=data, timeout=timeout, stream=stream) as response:
            return self.http.process_stream(response)
