import allure
from openai import OpenAI
from typing import Literal
from appauto.manager.error_manager.errors import ModelGibberishError
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class BaseValidator:
    @staticmethod
    def _if_gibberish(content) -> Literal["yes", "no"]:
        client = OpenAI(
            api_key="sk-lkxrwoxzkvjottwyuhxnosmivpxjnzhvlgpanemmmwlxpscw", base_url="https://api.siliconflow.cn/v1"
        )
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": """
    你是人类读者，完全从人类直观阅读感受出发，检测 3 类问题：
    1. 语义连贯性：是否存在上下文逻辑断裂、话题突兀跳转、前后表述矛盾, 导致读不懂或理解卡顿；
    2. 表达通顺度：是否存在句子结构生硬、语序混乱、读起来拗口、用词搭配不当，导致阅读不顺畅；
    3. 内容有效性：是否存在乱码符号、无意义字符、与文本核心无关的杂乱信息，影响阅读体验（一些合理的表情或 markdown 格式除外）。

    要求:
    1. 无需额外解释，仅回复「有」或「没有」
    2. 请你检测的内容来自 AI 大模型，可能有一些 markdown 格式或 think 标签之类的思考内容，这些都是合理情况
    3. 如果是数学题之类的，也不用做过多检测，只需要检测语义即可
    4. 如果内容为纯数字, 有可能是 ID 也有可能是乱码，需要自行判断是否为常见的 ID
    5. 由于用户提问时可能设置了 max-tokens, 因此如果内容戛然而止，此时应该不是问题，属于被合理截断。
    6. 如果内容反复重复，大概率是模型回答陷入死循环，此时也是有问题的。
                    """,
                },
                {"role": "user", "content": content},
            ],
            stream=True,
        )

        res = None
        for chunk in response:
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                res = chunk.choices[0].delta.content

        if "没有" in res:
            return "no"
        else:
            return "yes"

    @classmethod
    @allure.step("check_gibberish")
    def check_gibberish(cls, content):
        try:
            assert BaseValidator._if_gibberish(content) == "no"

        except AssertionError as e:
            logger.error(f"Model output gibberish: {str(e)}")
            raise ModelGibberishError(f"Model output gibberish: {str(e)}")

        except Exception as e:
            logger.error(f"error occurred while running ft sanity check: {str(e)}")
            raise e
