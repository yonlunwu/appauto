from time import time, sleep
from typing import Dict, List, TypeVar, Generic, Union, Literal
from enum import Enum
from uuid import uuid4
from random import choice
from tabulate import tabulate


from appauto.manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
)
from appauto.manager.config_manager import LoggingConfig

from testcases.amaas.gen_data import amaas, DefaultParams as DP

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)

logger = LoggingConfig.get_logger()


class ModelBaseTestResult(Enum):
    """
    模型基础检测状态
    """

    passed = "PASSED"
    failed = "FAILED"
    skipped = "SKIPPED"


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
    def scene_llm(cls, item: Dict, model_store: LLMModelStore):
        try:
            scene = [
                l
                for l in amaas.scene.llm
                if l.display_model_name == model_store.name or l.object_id == model_store.name
            ][0]
            model_store.question = str(uuid4())
            model_store.answer = scene.talk(model_store.question, stream=True, process_stream=True, max_tokens=None)

            item["question"] = model_store.question
            # item["answer"] = llm.answer

        except Exception as e:
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def scene_vlm(cls, item: Dict, model_store: VLMModelStore):
        try:
            scene = [
                v
                for v in amaas.scene.vlm
                if v.display_model_name == model_store.name or v.object_id == model_store.name
            ][0]
            model_store.question = "请解释这张图"
            model_store.answer = scene.talk(model_store.question, stream=True, max_tokens=None, process_stream=True)

            item["question"] = model_store.question
            # item["answer"] = vlm.answer

        except Exception as e:
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def scene_embedding(cls, item: Dict, model_store: EmbeddingModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.embedding
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = ["苹果", "小米", "香蕉", "公司"]
            model_store.answer = scene.talk(model_store.question, compute_similarity=True)

            item["question"] = model_store.question
            # item["answer"] = embedding.answer

        except Exception as e:
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def scene_rerank(cls, item: Dict, model_store: RerankModelStore):
        try:
            scene = [
                e
                for e in amaas.scene.rerank
                if e.display_model_name == model_store.name or e.object_id == model_store.name
            ][0]
            model_store.question = "叶文洁是谁"
            model_store.answer = scene.talk(model_store.question)

            item["question"] = model_store.question
            # item["answer"] = rerank.answer

        except Exception as e:
            model_store.query_result = ModelBaseTestResult.failed

        else:
            model_store.query_result = ModelBaseTestResult.passed

        finally:
            item["query_result"] = model_store.query_result

    @classmethod
    def stop(cls, model_store: T, type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]):

        # 查找目标模型
        target_model = next(
            m
            for m in getattr(amaas.model, type_)
            if m.display_model_name == model_store.name or m.object_id == model_store.name
        )

        target_model.stop()


class CommonModelBaseRunner:
    @classmethod
    def check_and_run_default_params_under_diff_tp(cls, tps: List[int], item: Dict, model_store: T):
        """
        不同 tp 情况下, 均按照默认参数检测 -> 拉起 -> 试验场景
        """
        item["name"] = model_store.name

        for tp in tps:
            params = CommonModelBaseStep.gen_params(item, model_store, tp)

            res = CommonModelBaseStep.model_store_check(item, model_store, params)
            if res.data.messages:
                continue  # check 失败

            CommonModelBaseStep.model_store_run(item, model_store, params)
            if model_store.run_result == ModelBaseTestResult.failed:
                continue  # run 失败

            match model_store:
                case LLMModelStore():
                    CommonModelBaseStep.scene_llm(item, model_store)
                    CommonModelBaseStep.stop(model_store, "llm")

                case VLMModelStore():
                    CommonModelBaseStep.scene_vlm(item, model_store)
                    CommonModelBaseStep.stop(model_store, "vlm")

                case EmbeddingModelStore():
                    CommonModelBaseStep.scene_embedding(item, model_store)
                    CommonModelBaseStep.stop(model_store, "embedding")

                case RerankModelStore():
                    CommonModelBaseStep.scene_rerank(item, model_store)
                    CommonModelBaseStep.stop(model_store, "rerank")

                case ParserModelStore():
                    CommonModelBaseStep.stop(model_store, "parser")

                case AudioModelStore():
                    CommonModelBaseStep.stop(model_store, "audio")

                case _:
                    logger.error(f"不支持的模型类型: {type(model_store)}, 跳过处理")

            sleep(5)


class DoCheck:
    @classmethod
    def check_default_run_result(self, models_store: List[T], items: List[Dict]):

        logger.info(tabulate(items, headers="keys", tablefmt="github"))

        for m_s in models_store:
            assert m_s.check_result == ModelBaseTestResult.passed
            assert m_s.run_result == ModelBaseTestResult.passed

            match m_s:
                case LLMModelStore() | VLMModelStore() | EmbeddingModelStore() | RerankModelStore():
                    assert m_s.query_result == ModelBaseTestResult.passed
