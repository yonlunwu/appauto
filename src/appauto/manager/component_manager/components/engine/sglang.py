import base64
from time import time
from ..amaas.base_component import BaseComponent
from ....config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class SGLang(BaseComponent):
    OBJECT_TOKEN = "sglang_id"

    POST_URL_MAP = dict(chat="v1/chat/completions")

    def talk_to_llm(
        self,
        content: str,
        model: str,
        stream=True,
        max_tokens: int = None,
        temperature: float = 0.6,
        top_p: int = 1,
        sys_promt_content=None,
        process_stream=True,
        timeout=None,
        encode_result=True,
        return_speed=False,
        measure_ttft=False,
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
        if return_speed:
            payload["return_speed"] = return_speed

        # 测量 ttft 时也等响应结束
        if measure_ttft:
            start = time()
            first_chunk = True
            ttft = None

            with self.post_without_token(
                "chat", json_data=payload, timeout=timeout, encode_result=False, stream=True
            ) as res:
                res.raise_for_status()
                for line in res.iter_lines():
                    if line:
                        logger.info(f"get res: {line}")
                        if first_chunk:
                            # 第一次接收到流数据，TTFT 达成
                            ttft = time() - start
                            logger.info(f"get ttft: {ttft}")
                            first_chunk = False

            return ttft

        # 不处理 stream(提取 stream 对应的文本)时根据是否 stream 决定是否 encode_result
        if not process_stream:
            encode_result = False if stream else encode_result
            return self.post_without_token(
                "chat", json_data=payload, timeout=timeout, encode_result=encode_result, stream=stream
            )

        # 处理 stream 时 stream 必须为 True
        else:
            with self.post_without_token("chat", json_data=payload, timeout=timeout, stream=True) as response:
                return self.http_without_token.process_stream_amaas(response)

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

    def talk_to_vlm(
        self,
        model: str,
        text: str = "请详细描述这张图片的内容，包括主体、颜色、场景等细节？",
        image_path: str = "src/appauto/assets/ci_test.image",
        stream=True,
        max_tokens: int = None,
        temperature: float = 0.6,
        top_p: int = 1,
        timeout=None,
        encode_result=True,
    ):
        assert image_path

        base64_data = self.image_to_base64(image_path)

        content = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": base64_data}}]

        payload = {
            "messages": [
                {"role": "system", "content": "你是图片分析助手，需结合图片内容和用户文本提问，给出详细回答。"},
                {"role": "user", "content": content},
            ],
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

        if stream:
            with self.post_without_token(
                "chat", json_data=payload, timeout=timeout, stream=True, encode_result=False
            ) as res:
                return self.http_without_token.process_stream_amaas(res)

        return self.post_without_token(
            "chat", json_data=payload, timeout=timeout, stream=False, encode_result=encode_result
        )
