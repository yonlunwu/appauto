from time import time
from ..amaas.base_component import BaseComponent
from ....config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


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
