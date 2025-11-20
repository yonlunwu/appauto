import pytest
from typing import List, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from appauto.manager.component_manager.components.amaas import AMaaS


class Requires:
    @staticmethod
    def need_have(amaas: "AMaaS", types: List[Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]]):
        req = [getattr(amaas.init_model_store, t) for t in types]
        return pytest.mark.skipif(not all(req), reason=f"need have: {types}")

    # TODO 要求 GPU 数量
    @staticmethod
    def need_gpu_count(amaas: "AMaaS", count: int):
        actual = len(amaas.workers[0].gpu_sum)
        return pytest.mark.skipif(actual < count, reason=f"The count of gpu({actual}) is less than needed({count})")
