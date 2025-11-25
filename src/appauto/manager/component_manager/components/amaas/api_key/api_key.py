from functools import cached_property

from ..base_component import BaseComponent


class APIKey(BaseComponent):

    OBJECT_TOKEN = "api_key"

    GET_URL_MAP = dict(get_self="/v1/kllm/api-keys", get_zhiwen_api_key="/v1/kllm/api-keys/zhiwen")

    POST_URL_MAP = dict(create="/v1/kllm/api-keys")

    DELETE_URL_MAP = dict(delete="/v1/kllm/api-keys/{api_key}")

    def refresh(self, alias=None):
        res = super().refresh(alias)
        self.data = [item for item in res.data.get("items") if item.id == self.object_id][0]
        return res

    def delete(self, timeout: int = None):
        return self.delete("delete", timeout=timeout)

    @cached_property
    def value(self) -> str:
        return self.data.value
