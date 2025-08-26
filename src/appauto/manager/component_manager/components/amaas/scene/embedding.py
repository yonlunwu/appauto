from typing import Literal, List, Union
from ....base_component import BaseComponent


class Embedding(BaseComponent):
    OBJECT_TOKEN = "embedding_id"

    GET_URL_MAP = dict(get_models="/v1/models")

    POST_URL_MAP = dict(chat="/v1/embeddings", compute_similarity="/v1/kllm/embedding/compute_similarity")

    def talk(
        self,
        content: Union[List, str],
        model: str = None,
        encoding_format: Literal["float", "base64"] = "float",
        dimensions: int = 0,
        timeout=None,
        compute_similarity=True,
    ):
        data = {
            "input": content if isinstance(content, list) else [content],
            "model": model or self.object_id,
            "encoding_format": encoding_format,
            "dimensions": dimensions,
        }

        res = self.post("chat", json_data=data, timeout=timeout, encode_result=True)

        if compute_similarity:
            num = len(res.data)
            vectors = []
            for i in range(num):
                vectors.append([in_d.embedding for in_d in res.data if in_d.index == i][0])

            res = self.compute_similarity(num, vectors, timeout)

        return res

    def compute_similarity(self, num: int, vectors: List[List], timeout=None):
        data = {"num": num, "dimension": 1024, "vectors": vectors}

        return self.post("compute_similarity", json_data=data, timeout=timeout, encode_result=True)

    @property
    def display_model_name(self):
        return self.data.display_model_name

    @property
    def object(self) -> Literal["model"]:
        return self.data.object

    @property
    def owned_by(self) -> Literal["AMES"]:
        return self.data.owned_by

    @property
    def meta(self) -> Literal[None]:
        return self.data.meta
