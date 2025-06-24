"""
1. 拉代码 (ftransformers)
2. 安装 ft
3. 起服务
4. 测试 api
5. 停服务
"""

"""
- max_tokens: int & > 0
- temperature: ≥ 0
- top_p: (0, 1]
"""

# TODO
"""
1. 完善 promp_list, 比如加上 guoheng 一测就崩的
2. 完善用例判定标准
3. 测试区分正常场景和异常场景 (比如分为 2 个类)
4. 补充要测试的 model
"""

import pytest
import allure
from random import choice
from appauto.manager.connection_manager.ssh import SSHClient
from appauto.manager.client_manager import BaseLinux
from testcases.ftransformers.gen_data import sglang


prompt_list = [
    "Please elaborate on modern world history.",
    "Please introduce Harry Potter.",
    "I want to learn Python. Please give me some advice.",
    "Please tell me a joke ",
    "如果所有的猫都是动物，而一些动物是狗，那么可以得出什么结论？",
    "有一个房间里有三盏灯，外面有三个开关。你只能进房间一次，如何确定哪个开关对应哪盏灯？",
    "健康饮食的基本原则是什么？",
    "请推荐一些适合家庭旅行的目的地。",
    "如何提高个人网络安全？",
    "什么是认知失调理论？请举例说明。",
    "供求法则是什么？它如何影响市场价格？",
    " 请简要介绍一下工业革命的影响。",
    "请分析《红楼梦》的主题和主要人物。",
    "什么是印象派艺术？请列举一些著名的印象派画家。",
    "如何定义古典音乐与流行音乐的区别？",
    "请解答方程 2x+3=11。",
    "如何计算一个圆的面积？请给出公式并解释。",
    "什么是概率密度函数？请举例说明。",
    "什么是机器学习？它与人工智能有什么区别？",
    "DNA的结构是什么？它是如何携带遗传信息的？",
    "请解释一下相对论的基本概念。",
]


"""
单个测试:
    DeepSeek-R1-GGUF-Q4_K_M
        - stream: true | false.                                                        = 2
        - max_tokens: 512 | 10 | 1 | -1 | 5.0                                          = 5 
        - temperature: no temperature and no top_p | 0 | 1.0 | 2.0 | -1                = 5
        - top_p: no temperature and no top_p | 0 | 1 | -0.5                            = 4

批量测试:
    DeepSeek-R1-GGUF-Q4_K_M
        - concurrent: 4 | 128
        - prompt_lens: 1024 | 8192
        - max_tokens: 128
"""


@allure.epic("TestSGLangAPISingle")
@pytest.mark.night
class TestSGLangAPISingle:
    def test_stream_false(self):
        """
        测试 stream=False 时可以正常工作.
        """
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=False,
            max_tokens=choice(
                [-1, 0, 1, 5.0, 10, 512, 1024, 131072]
            ),  # 必须 > 0，# 0.5 会直接 500 Internal Server Error
            temperature=choice([-1, 0, 1.0, 2.0, 1024, None]),  # 必须 ≥ 0
            top_p=choice([0, -0.5, 0.5, 1, 1024, None]),
        )

    def test_stream_true_and_process_stream_correct(self):
        """测试 stream=True 时可以正常工作: 参数正确"""
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=True,
            max_tokens=choice([1024]),
            temperature=choice([None]),
            top_p=choice([None]),
            process_stream=True,
        )

    def test_stream_true_and_process_stream_random(self):
        """测试 stream=True 时可以正常工作: 参数随机"""
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=True,
            max_tokens=choice([-1, 0, 1, 5.0, 10, 512, 1024, 131072]),
            temperature=choice([0, -1, 1.0, 2.0, None]),
            top_p=choice([0, -0.5, 0.5, 1, None]),
            process_stream=True,
        )

    # max_token = 0 时用中文提问，遇到一次用英文回答
    @pytest.mark.parametrize(
        "max_tokens", [-1, 0, 1, 5.0, 10, 512, 1024, 131072]
    )  # 必须 > 0，# 0.5 会直接 500 Internal Server Error
    def test_max_tokens(self, max_tokens):
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=choice([True, False]),
            max_tokens=max_tokens,
            temperature=choice([0, -1, 1.0, 2.0, None]),
            top_p=choice([0, -0.5, 0.5, 1, None]),
        )

    def test_no_temperature_and_no_top_p(self):
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=choice([True, False]),
            max_tokens=choice([-1, 0, 1, 5.0, 10, 512, 1024, 131072]),
            temperature=None,
            top_p=None,
        )

    @pytest.mark.parametrize(
        "temperature", [-1, 0, 1.0, 2.0, 1024, None]
    )  # temperature 必须非负, 会返回 200, error_msg 套在 response 中, 可以是 float
    def test_temperature(self, temperature):
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=choice([True, False]),
            max_tokens=choice([-1, 0, 1, 5.0, 10, 512, 1024]),
            temperature=temperature,
            top_p=choice([0, -0.5, 0.5, 1, None]),
        )

    @pytest.mark.parametrize("top_p", [0, -0.5, 0.5, 1, 1.0, 1.0000000000000001, 1024, None])
    def test_top_p(self, top_p):
        """
        top_p must be in (0, 1]
            - top_p 位于合理值 rc == 200;
            - 不合理时 rc == 400
        """
        sglang.talk(
            content=choice(prompt_list),
            model="DeepSeek-R1",
            stream=choice([True, False]),
            max_tokens=choice([-1, 0, 1, 5.0, 10, 512, 1024]),
            temperature=choice([0, -1, 1.0, 2.0, None]),
            top_p=top_p,
        )

    # def test_long_text(self):
    #     """长文本提问"""
    #     ...
