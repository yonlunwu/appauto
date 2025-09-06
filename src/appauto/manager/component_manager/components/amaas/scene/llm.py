from typing import Literal
from .base import BaseScene


class LLM(BaseScene):
    def talk(
        self,
        content: str,
        model: str = None,
        stream=True,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        timeout=None,
        process_stream=True,
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
            "top_p": top_p,
            "stream": stream,
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        process_stream = process_stream if stream else False
        encode_result = False if stream else encode_result

        if stream:
            with self.post("llm_vlm", stream=stream, json_data=data, timeout=timeout) as res:
                return self.http.process_stream_amaas(res) if process_stream else res

        return self.post("llm_vlm", json_data=data, timeout=timeout, stream=stream, encode_result=encode_result)
