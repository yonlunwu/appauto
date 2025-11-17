import pytest
from time import sleep
from enum import Enum
from uuid import uuid4
from faker import Faker
from openai import OpenAI
from random import choice
from tabulate import tabulate
from typing import Dict, List, TypeVar, Literal, Type


from appauto.manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
    BaseModelStore,
)
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.error_manager import ModelStoreCheckError, ModelStoreRunError

from testcases.amaas.gen_data import amaas, DefaultParams as DP

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)

logger = LoggingConfig.get_logger()


@pytest.fixture(autouse=True)
def global_fixture_for_model_base_test():

    model_store_types: tuple[Type[T], ...] = T.__constraints__

    attributes = ["check_result", "run_result", "query_result"]

    for store_type in model_store_types:
        for attr in attributes:
            setattr(store_type, attr, None)


class ModelBaseTestResult(Enum):
    """
    模型基础检测状态
    """

    passed = "PASSED"
    failed = "FAILED"
    skipped = "SKIPPED"


class CommonModelPerformenceStep:
    @classmethod
    def gen_text_with_length(
        cls, length: int, language: Literal["en_US", "fr_FR", "de_DE", "es_ES", "ja_JP", "ru_RU"] = None
    ):
        """生成指定长度的文本"""
        language = language or choice(["en_US", "fr_FR", "de_DE", "es_ES", "ja_JP", "ru_RU"])

        fake = Faker(language)

        text = ""

        while len(text) < length:
            # 每次生成一段文本，每次最多 512 个字符
            text += fake.text(max_nb_chars=DP.max_nb_chars) + ""

        return text


class CommonModelBaseStep:

    @classmethod
    def gen_params(cls, result_item: Dict, model_store: T, tp: int) -> Dict:
        result_item["name"] = model_store.name
        result_item["tp"] = tp
        rule: Dict = model_store.get_run_rule()

        worker = choice(amaas.workers)
        result_item["worker"] = f"{worker.name}/{worker.object_id}"

        params = dict(
            worker_id=worker.object_id,
            tp=tp,
            access_limit=rule.data.access_limit,
        )

        match model_store:
            case LLMModelStore() | VLMModelStore() | EmbeddingModelStore() | RerankModelStore():
                params["max_total_tokens"] = rule.data.max_total_tokens

        return params

    @classmethod
    def model_store_check(cls, result_item: Dict, model_store: T, params: Dict) -> Dict:
        res = model_store.check(**params)

        model_store.check_result = ModelBaseTestResult.passed
        result_item["check_result"] = model_store.check_result

        if res.data.messages:
            model_store.check_result = ModelBaseTestResult.failed
            model_store.run_result = ModelBaseTestResult.skipped
            result_item["check_result"] = model_store.check_result
            result_item["run_result"] = model_store.run_result

        return res

    @classmethod
    def model_store_run(cls, result_item: Dict, model_store: T, params: Dict):
        try:
            model_store.run(wait_for_running=True, running_timeout_s=DP.wait_model_running_timeout_s, **params)

        except (RuntimeError, TimeoutError) as e:
            model_store.run_result = ModelBaseTestResult.failed

        else:
            model_store.run_result = ModelBaseTestResult.passed

        finally:
            result_item["run_result"] = model_store.run_result

    @classmethod
    def scene_and_stop(cls, model_store: T, result_item: Dict, skip_scene=False):
        """有些模型有试验场景, 有些没有"""
        match model_store:
            case LLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_llm(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "llm")

            case VLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_vlm(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "vlm")

            case EmbeddingModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_embedding(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "embedding")

            case RerankModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_rerank(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "rerank")

            case ParserModelStore():
                CommonModelBaseStep._scene_parser(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "parser")

            case AudioModelStore():
                CommonModelBaseStep._scene_audio(result_item, model_store)
                CommonModelBaseStep.stop(model_store, "audio")

            case _:
                logger.error(f"不支持的模型类型: {type(model_store)}, 跳过处理")

    @classmethod
    def _scene_llm(cls, result_item: Dict, model_store: LLMModelStore):
        try:
            scene = [
                l
                for l in amaas.scene.llm
                if l.display_model_name == model_store.name or l.object_id == model_store.name
            ][0]
            # model_store.question = str(uuid4())
            questions = [
                "35+25+10=60，对吗？",
                "天空为什么是蓝色的？",
                "Wish you happiness each day and all the best in everything",
                "用python写冒泡排序的代码，关键处请添加注释",
                "写愤怒的小鸟的代码",
                "请给我一份周末北京旅游攻略，去什么景点吃什么走什么路线有什么注意事项都写的详细一些",
            ]

            for q in questions:
                model_store.question = q
                model_store.answer = scene.talk(model_store.question, stream=True, process_stream=True, max_tokens=2048)

                result_item["question"] = model_store.question
                # item["answer"] = llm.answer

                assert DoCheck.check_gibberish(model_store.answer) == "no"

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed, error: {str(e)}")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            result_item["query_result"] = model_store.query_result

    @classmethod
    def _scene_vlm(cls, result_item: Dict, model_store: VLMModelStore):
        try:
            scene = [
                v
                for v in amaas.scene.vlm
                if v.display_model_name == model_store.name or v.object_id == model_store.name
            ][0]
            model_store.question = "请解释这张图"
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, stream=True, max_tokens=None, process_stream=True)

                result_item["question"] = model_store.question
                # item["answer"] = vlm.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            result_item["query_result"] = model_store.query_result

    @classmethod
    def _scene_embedding(cls, result_item: Dict, model_store: EmbeddingModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.embedding
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = ["苹果", "小米", "香蕉", "公司"]
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, compute_similarity=True)

                result_item["question"] = model_store.question
                # item["answer"] = embedding.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            result_item["query_result"] = model_store.query_result

    @classmethod
    def _scene_rerank(cls, result_item: Dict, model_store: RerankModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.rerank
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = "叶文洁是谁"
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question)

                result_item["question"] = model_store.question
                # item["answer"] = rerank.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            result_item["query_result"] = model_store.query_result

    @classmethod
    def _scene_parser(cls, result_item: Dict, model_store: ParserModelStore):
        model_store.query_result = ModelBaseTestResult.skipped
        result_item["query_result"] = model_store.query_result

    @classmethod
    def _scene_audio(cls, result_item: Dict, model_store: AudioModelStore):
        model_store.query_result = ModelBaseTestResult.skipped
        result_item["query_result"] = model_store.query_result

    @classmethod
    def stop(cls, model_store: T, type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]):

        if model_list := getattr(amaas.model, type_, None):
            if target_models := [
                m for m in model_list if m.display_model_name == model_store.name or m.name == model_store.name
            ]:
                for t_m in target_models:
                    # TODO 当前存在副本残留的 bug, 后面修复后要删除这里的逻辑, 预期 model.stop 要停止所有的副本
                    if len(all_ins := t_m.instances) > 1:
                        for ins in all_ins[:-1]:
                            logger.info(f"instance_name: {ins}")
                            ins.stop()

                    t_m.stop()


class CommonModelBaseRunner:
    @classmethod
    def get_models_store(
        cls, model_store_type: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]
    ) -> List[BaseModelStore]:
        return getattr(amaas.init_model_store, model_store_type)

    @classmethod
    def run_with_default(cls, tp: Literal[1, 2, 4, 8], model_store: T):
        """
        默认参数检测 -> 拉起 -> 试验场景
        """
        result_item = {}

        try:

            logger.info(f"test model store: {model_store.name}, tp: {tp}, id: {model_store.object_id}".center(150, "="))
            params = CommonModelBaseStep.gen_params(result_item, model_store, tp)

            # check 失败后直接记录结果
            res = CommonModelBaseStep.model_store_check(result_item, model_store, params)
            if res.data.messages:
                raise ModelStoreCheckError(f"model store: {model_store.name}, tp: {tp}, check failed")

            # run 失败了要主动 stop，不要影响其他的
            CommonModelBaseStep.model_store_run(result_item, model_store, params)
            if model_store.run_result == ModelBaseTestResult.failed:
                raise ModelStoreRunError(f"model store: {model_store.name}, tp: {tp}, run failed")

            CommonModelBaseStep.scene_and_stop(model_store, result_item)

            sleep(5)

        except ModelStoreCheckError:
            logger.error(f"model store: {model_store.name}, tp: {tp}, check failed")

        except ModelStoreRunError:
            logger.error(f"model store: {model_store.name}, tp: {tp}, run failed")
            CommonModelBaseStep.scene_and_stop(model_store, result_item, skip_scene=True)

        except Exception as e:
            logger.error(
                f"error occurred in check_and_run_default_params_under_diff_tp, "
                f"model: {model_store.name} tp: {tp}, error: {e}"
            )
            raise e

        finally:
            return result_item


class DoCheck:
    @classmethod
    def check_final_item(cls, item: Dict):
        """
        测试结束后统一检查是否存在 failed item.
        """

        logger.info(tabulate([item], headers="keys", tablefmt="github"))

        assert item["check_result"] == ModelBaseTestResult.passed
        assert item["run_result"] == ModelBaseTestResult.passed

        assert item["query_result"] in [ModelBaseTestResult.passed, ModelBaseTestResult.skipped]

    @classmethod
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
