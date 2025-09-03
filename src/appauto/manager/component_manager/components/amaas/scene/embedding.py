from typing import Literal, List, Union
from .base import BaseScene


class Embedding(BaseScene):

    def talk(
        self,
        content: Union[List, str],
        model: str = None,
        encoding_format: Literal["float", "base64"] = "float",
        dimensions: int = 0,
        compute_similarity=True,
        timeout=None,
    ):
        data = {
            "input": content if isinstance(content, list) else [content],
            "model": model or self.object_id,
            "encoding_format": encoding_format,
            "dimensions": dimensions,
        }

        res = self.post("embedding", json_data=data, timeout=timeout, encode_result=True)

        if compute_similarity:
            num = len(res.data)
            vectors = []
            for i in range(num):
                vectors.append([in_d.embedding for in_d in res.data if in_d.index == i][0])

            res = self.compute_similarity(num, vectors, timeout)

        return res

    def compute_similarity(self, num: int, vectors: List[List], timeout=None):
        data = {"num": num, "dimension": 1024, "vectors": vectors}

        return self.post("embedding_compute_similarity", json_data=data, timeout=timeout, encode_result=True)
