import re
from typing import List, TypeVar

T = TypeVar("T")


class CustomList(List[T]):
    def _match_all(self, item, **kwargs):
        return all([re.match(f"^{value}$", str(getattr(item, name))) for name, value in kwargs.items()])

    def _match_any(self, item, **kwargs):
        return any([re.match(f"^{value}$", str(getattr(item, name))) for name, value in kwargs.items()])

    def filter(self, index: slice = None, OR: dict = None, **kwargs) -> List[T]:
        result = CustomList()
        funcs = {id(OR): self._match_any, id(kwargs): self._match_all}

        for item in self:
            if all(funcs[id(c)](item, **c) for c in [OR, kwargs] if c):
                result.append(item)

        if index:
            result = CustomList(result[index])
        return result
