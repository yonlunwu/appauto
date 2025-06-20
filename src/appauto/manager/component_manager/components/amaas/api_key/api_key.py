from ....base_component import BaseComponent


class APIKey(BaseComponent):

    OBJECT_TOKEN = "api_key"

    GET_URL_MAP = dict(list_all="/v1/kllm/api-keys", get_zhiwen_api_key="/v1/kllm/api-keys/zhiwen")

    POST_URL_MAP = dict(create="/v1/kllm/api-keys")

    DELETE_URL_MAP = dict(delete="/v1/kllm/api-keys/{api_key}")

    def delete(self, timeout: int = None):
        return self.delete("delete", timeout=timeout)
