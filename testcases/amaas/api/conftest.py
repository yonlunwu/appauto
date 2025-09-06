import pytest
from time import sleep
from enum import Enum
from uuid import uuid4
from faker import Faker
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
)
from appauto.manager.config_manager import LoggingConfig

from testcases.amaas.gen_data import amaas

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)

logger = LoggingConfig.get_logger()


@pytest.fixture(scope="function", autouse=False)
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
        length = length * 1.2

        while len(text) < length:
            # 每次生成一段文本，每次最多 512 个字符
            text += fake.text(max_nb_chars=512) + ""

        return text[:length]


class CommonModelBaseStep:

    @classmethod
    def gen_params(cls, item: Dict, model_store: T, tp: int) -> Dict:
        item["tp"] = tp
        rule: Dict = model_store.get_run_rule()

        worker = choice(amaas.workers)
        item["worker"] = f"{worker.name}/{worker.object_id}"

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
    def model_store_check(cls, item: Dict, model_store: T, params: Dict) -> Dict:
        res = model_store.check(**params)

        model_store.check_result = ModelBaseTestResult.passed
        item["check_result"] = model_store.check_result

        if res.data.messages:
            model_store.check_result = ModelBaseTestResult.failed
            model_store.run_result = ModelBaseTestResult.skipped
            item["check_result"] = model_store.check_result
            item["run_result"] = model_store.run_result

        return res

    @classmethod
    def model_store_run(cls, item: Dict, model_store: T, params: Dict):
        try:
            model_store.run(wait_for_running=True, running_timeout_s=900, **params)

        except RuntimeError or TimeoutError as e:
            model_store.run_result = ModelBaseTestResult.failed

        else:
            model_store.run_result = ModelBaseTestResult.passed

        finally:
            item["run_result"] = model_store.run_result

    @classmethod
    def scene_and_stop(cls, model_store: T, item: Dict, skip_scene=False):
        """有些模型有试验场景, 有些没有"""
        match model_store:
            case LLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_llm(item, model_store)
                CommonModelBaseStep.stop(model_store, "llm")

            case VLMModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_vlm(item, model_store)
                CommonModelBaseStep.stop(model_store, "vlm")

            case EmbeddingModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_embedding(item, model_store)
                CommonModelBaseStep.stop(model_store, "embedding")

            case RerankModelStore():
                if not skip_scene:
                    CommonModelBaseStep._scene_rerank(item, model_store)
                CommonModelBaseStep.stop(model_store, "rerank")

            case ParserModelStore():
                CommonModelBaseStep._scene_parser(item, model_store)
                CommonModelBaseStep.stop(model_store, "parser")

            case AudioModelStore():
                CommonModelBaseStep._scene_audio(item, model_store)
                CommonModelBaseStep.stop(model_store, "audio")

            case _:
                logger.error(f"不支持的模型类型: {type(model_store)}, 跳过处理")

    @classmethod
    def _scene_llm(cls, item: Dict, model_store: LLMModelStore):
        try:
            scene = [
                l
                for l in amaas.scene.llm
                if l.display_model_name == model_store.name or l.object_id == model_store.name
            ][0]
            model_store.question = str(uuid4())
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, stream=True, process_stream=True, max_tokens=None)

                item["question"] = model_store.question
                # item["answer"] = llm.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def _scene_vlm(cls, item: Dict, model_store: VLMModelStore):
        try:
            scene = [
                v
                for v in amaas.scene.vlm
                if v.display_model_name == model_store.name or v.object_id == model_store.name
            ][0]
            model_store.question = "请解释这张图"
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, stream=True, max_tokens=None, process_stream=True)

                item["question"] = model_store.question
                # item["answer"] = vlm.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def _scene_embedding(cls, item: Dict, model_store: EmbeddingModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.embedding
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = ["苹果", "小米", "香蕉", "公司"]
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question, compute_similarity=True)

                item["question"] = model_store.question
                # item["answer"] = embedding.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def _scene_rerank(cls, item: Dict, model_store: RerankModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.rerank
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = "叶文洁是谁"
            for _ in range(3):
                model_store.answer = scene.talk(model_store.question)

                item["question"] = model_store.question
                # item["answer"] = rerank.answer

        except Exception as e:
            logger.info(f"model store: {model_store.name}, scene failed")
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def _scene_parser(cls, item: Dict, model_store: ParserModelStore):
        model_store.query_result = ModelBaseTestResult.skipped
        item["query_result"] = model_store.query_result

    @classmethod
    def _scene_audio(cls, item: Dict, model_store: AudioModelStore):
        model_store.query_result = ModelBaseTestResult.skipped
        item["query_result"] = model_store.query_result

    @classmethod
    def stop(cls, model_store: T, type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]):

        if model_list := getattr(amaas.model, type_, None):
            if target_models := [
                m for m in model_list if m.display_model_name == model_store.name or m.object_id == model_store.name
            ]:
                for t_m in target_models:
                    # TODO 当前存在副本残留的 bug, 后面修复后要删除这里的逻辑, 预期 model.stop 要停止所有的副本
                    if len(all_ins := t_m.instances) > 1:
                        for ins in all_ins[:-1]:
                            ins.stop()

                    t_m.stop()


class CommonModelBaseRunner:
    @classmethod
    def check_and_run_default_params_under_diff_tp(cls, tps: List[int], items: List[Dict], item: Dict, model_store: T):
        """
        不同 tp 情况下, 均按照默认参数检测 -> 拉起 -> 试验场景
        """
        item["name"] = model_store.name

        for tp in tps:

            try:

                logger.info(
                    f"test model store: {model_store.name}, tp: {tp}, id: {model_store.object_id}".center(150, "=")
                )
                params = CommonModelBaseStep.gen_params(item, model_store, tp)

                res = CommonModelBaseStep.model_store_check(item, model_store, params)
                # check 失败
                if res.data.messages:
                    logger.info(f"model store: {model_store.name}, tp: {tp}, check failed")
                    continue

                CommonModelBaseStep.model_store_run(item, model_store, params)
                # run 失败
                if model_store.run_result == ModelBaseTestResult.failed:
                    logger.info(f"model store: {model_store.name}, tp: {tp}, run failed")
                    # run 失败了要 stop 掉，不要影响其他的
                    CommonModelBaseStep.scene_and_stop(model_store, item, skip_scene=True)
                    continue

                CommonModelBaseStep.scene_and_stop(model_store, item)

                sleep(5)

            except Exception as e:
                logger.error(
                    f"error occurred in check_and_run_default_params_under_diff_tp, "
                    f"model: {model_store.name} tp: {tp}, error: {e}"
                )
                raise e

            # # TODO 这里 assert 后中间的失败了，后面还没被 for 的就测不上了，因此这里不再 check 了，而是放在最后统一 check items
            finally:
                # DoCheck.check_default_run_result(model_store, [item])
                items.append(item)


class DoCheck:
    @classmethod
    def check_default_run_result(cls, model_store: T, item: List[Dict]):
        """
        模型的每个 tp 都需要 check.
        """
        logger.info(tabulate(item, headers="keys", tablefmt="github"))

        assert model_store.check_result == ModelBaseTestResult.passed
        assert model_store.run_result == ModelBaseTestResult.passed

        match model_store:
            case LLMModelStore() | VLMModelStore() | EmbeddingModelStore() | RerankModelStore():
                assert model_store.query_result == ModelBaseTestResult.passed

    @classmethod
    def check_final_items(cls, items: List[Dict]):
        """
        测试结束后统一检查是否存在 failed item.
        """

        logger.info(tabulate(item, headers="keys", tablefmt="github"))

        for item in items:
            assert item["check_result"] == ModelBaseTestResult.passed
            assert item["run_result"] == ModelBaseTestResult.passed

            assert item["query_result"] in [ModelBaseTestResult.passed, ModelBaseTestResult.skipped]
