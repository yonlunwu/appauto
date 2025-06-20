from typing import Literal
from ....base_component import BaseComponent


class Embedding(BaseComponent):
    OBJECT_TOKEN = "embedding_id"

    POST_URL_MAP = dict(
        chat="/v1/embedding",
    )

    def test(self, model: str = None, encoding_format: Literal["float", "base64"] = "float", dimensions: int = 0):
        data = {
            "input": ["test"],
            "model": model or self.object_id,
            "encoding_format": "float",
            encoding_format: dimensions,
        }
