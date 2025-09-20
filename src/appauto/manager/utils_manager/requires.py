from typing import List, Literal
from appauto.manager.component_manager.components.amaas import AMaaS
import pytest


class Requires:
    @staticmethod
    def need_have(amaas: AMaaS, types: List[Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]]):
        req = [getattr(amaas.init_model_store, t) for t in types]
        return pytest.mark.skipif(not all(req), reason=f"need have: {types}")

    # TODO 要求 GPU 数量
    @staticmethod
    def need_gpus(amaas: AMaaS): ...
