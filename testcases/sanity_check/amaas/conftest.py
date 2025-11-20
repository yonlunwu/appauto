import allure
import pytest
from openai import OpenAI
from random import sample
from typing import TypeVar, Literal


from appauto.manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
)
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.error_manager.errors import OperationNotSupported

from testcases.sanity_check.amaas.gen_data import amaas, DefaultParams as DP


T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)

logger = LoggingConfig.get_logger()


@pytest.fixture(autouse=True)
def global_fixture_for_amaas_ci_sanity_check():
    # TODO 是否要优先 stop 所有模型
    amaas.api.wait_gpu_release(interval_s=20, timeout_s=180)


class CommonModelBaseStep:
    @classmethod
    @allure.step("scene_and_stop")
    def scene_and_stop(cls, model_store: T, skip_scene=False):
        """有些模型有试验场景, 有些没有"""
        match model_store:
            case LLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_llm(model_store)
                CommonModelBaseStep.stop(model_store, "llm")

            case VLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_vlm(model_store)
                CommonModelBaseStep.stop(model_store, "vlm")

            case EmbeddingModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_embedding(model_store)
                CommonModelBaseStep.stop(model_store, "embedding")

            case RerankModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_rerank(model_store)
                CommonModelBaseStep.stop(model_store, "rerank")

            case ParserModelStore():
                CommonModelBaseStep._scene_parser(model_store)
                CommonModelBaseStep.stop(model_store, "parser")

            case AudioModelStore():
                CommonModelBaseStep._scene_audio(model_store)
                CommonModelBaseStep.stop(model_store, "audio")

            case _:
                logger.error(f"unsupport model type: {type(model_store)}, skip.")

    @classmethod
    @allure.step("_scene_llm")
    def _scene_llm(cls, model_store: LLMModelStore):
        try:
            scene = [
                l
                for l in amaas.api.scene.llm
                if l.display_model_name == model_store.name or l.object_id == model_store.name
            ][0]

            for q in sample(DP.llm_questions, 3):
                model_store.question = q
                model_store.answer = scene.talk(
                    model_store.question, stream=True, process_stream=True, max_tokens=2048, timeout=300
                )

                assert DoCheck.check_gibberish(model_store.answer) == "no"

        except Exception as e:
            logger.info(f"scene failed, model store: {model_store.name}, error: {str(e)}")
            raise e

    @classmethod
    @allure.step("_scene_vlm")
    def _scene_vlm(cls, model_store: VLMModelStore):
        try:
            scene = [
                v
                for v in amaas.api.scene.vlm
                if v.display_model_name == model_store.name or v.object_id == model_store.name
            ][0]
            model_store.question = "请解释这张图"
            for _ in range(3):
                model_store.answer = scene.talk(
                    model_store.question, stream=True, max_tokens=None, process_stream=True, timeout=300
                )

        except Exception as e:
            logger.info(f"scene failed, model store: {model_store.name}, error: {str(e)}")
            raise e

    @classmethod
    @allure.step("_scene_embedding")
    def _scene_embedding(cls, model_store: EmbeddingModelStore):
        try:
            scene = [
                e
                for e in amaas.api.scene.embedding
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = ["苹果", "小米", "香蕉", "公司"]
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, compute_similarity=True, timeout=300)

        except Exception as e:
            logger.info(f"scene failed, model store: {model_store.name}, error: {str(e)}")
            raise e

    @classmethod
    @allure.step("_scene_rerank")
    def _scene_rerank(cls, model_store: RerankModelStore):
        try:
            scene = [
                e
                for e in amaas.api.scene.rerank
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = "叶文洁是谁"
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, timeout=300)

        except Exception as e:
            logger.info(f"scene failed, model store: {model_store.name}, error: {str(e)}")
            raise e

    @classmethod
    @allure.step("_scene_parser")
    def _scene_parser(cls, model_store: ParserModelStore):
        pass

    @classmethod
    @allure.step("_scene_audio")
    def _scene_audio(cls, model_store: AudioModelStore):
        pass

    @classmethod
    @allure.step("stop")
    def stop(cls, model_store: T, type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]):

        if model_list := getattr(amaas.api.model, type_, None):
            if target_models := [
                m for m in model_list if m.display_model_name == model_store.name or m.name == model_store.name
            ]:
                for t_m in target_models:
                    t_m.stop()

    # TODO 确认是否适配其他类型模型
    @classmethod
    @allure.step("launch_model")
    def launch_model(cls, model_store: T, tp: Literal[1, 2, 4, 8]):
        try:
            amaas.api.launch_model_with_default(tp, model_store)
        except OperationNotSupported as e:
            logger.info(f"{str(e)}")
            pytest.skip(str(e))
        except Exception as e:
            logger.error(f"error occurred while launch model: {str(e)}")
            raise e

    @classmethod
    def check_model_priority(cls, model_store: T): ...


class DoCheck:
    @classmethod
    @allure.step("check_gibberish")
    def check_gibberish(cls, content) -> Literal["yes", "no"]:
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
