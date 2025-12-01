from pathlib import Path
from .base import BaseScene


import base64


class VLM(BaseScene):
    OBJECT_TOKEN = "rerank_id"
    DEFAULT_IMAGE = str(Path(__file__).resolve().parents[5] / "assets" / "ci_test.image")

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
        image_path: str = None,
        stream=True,
        max_tokens: int = 1024,
        top_p: int = 1,
        model: str = None,
        timeout=None,
        encode_result=False,
        process_stream=True,
    ):
        image_path = image_path or self.DEFAULT_IMAGE
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
            "top_p": top_p,
            "stream": stream,
        }

        if max_tokens:
            data["max_tokens"] = max_tokens

        process_stream = process_stream if stream else False
        encode_result = False if stream else encode_result

        if stream:
            with self.post("llm_vlm", stream=True, json_data=data, timeout=timeout) as res:
                return self.http.process_stream_amaas(res, process_chunk=False) if process_stream else res

        return self.post("llm_vlm", json_data=data, timeout=timeout, stream=False, encode_result=encode_result)
