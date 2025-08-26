from typing import Literal, List, Union
from ....base_component import BaseComponent


import base64


class MultiModel(BaseComponent):
    OBJECT_TOKEN = "rerank_id"

    GET_URL_MAP = dict(get_models="/v1/models")

    POST_URL_MAP = dict(chat="/v1/chat/completions")

    @classmethod
    def image_to_base64(cls, image_path="/Users/ryanyang/Desktop/WechatIMG1.jpeg"):
        """
        将图片文件转换为Base64编码的二进制数据

        参数:
            image_path: 图片文件的路径

        返回:
            图片的Base64编码二进制数据，如果出错则返回None
        """
        try:
            # 以二进制模式读取图片文件
            with open(image_path, "rb") as image_file:
                # 读取图片的二进制数据
                image_data = image_file.read()

                # 将二进制数据编码为Base64格式
                base64_bytes = base64.b64encode(image_data)

                base64_str = base64_bytes.decode("utf-8")

                return base64_str

        except FileNotFoundError:
            raise RuntimeError(f"错误: 找不到文件 {image_path}")
        except Exception as e:
            raise RuntimeError(f"转换过程中发生错误: {str(e)}")

    def talk(
        self,
        text: str = "请解释这张图",
        image_path: str = "/Users/ryanyang/Desktop/WechatIMG1.jpeg",
        stream=True,
        max_tokens: int = 1024,
        top_p: int = 1,
        model: str = None,
        timeout=None,
        encode_result=False,
        process_stream=False,
    ):
        assert image_path

        base64_data = self.image_to_base64(image_path)

        data = {
            "messages": [
                {
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_data}"},
                        },
                    ],
                    "role": "user",
                }
            ],
            "model": model or self.object_id,
            "temperature": 1,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        process_stream = process_stream if stream else False
        encode_result = False if stream else encode_result

        if stream:
            with self.post("chat", stream=stream, json_data=data, timeout=timeout) as res:
                return self.http.process_stream_amaas(res, process_chunk=False) if process_stream else res

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
