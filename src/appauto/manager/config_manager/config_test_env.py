from typing import Dict
from functools import cached_property


# TODO 收集环境信息
class TestEnvCOnfig:
    def __init__(self, version=None, model=None):
        self.model = model
        self.version = version

    @cached_property
    def data(self) -> Dict:
        return {"model": self.model, "version": self.version}
