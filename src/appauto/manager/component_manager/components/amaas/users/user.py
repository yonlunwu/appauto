from ....base_component import BaseComponent


class AMaaSUser(BaseComponent):
    OBJECT_TOKEN = "user_id"

    GET_URL_MAP = dict(list_all="/v1/kllm/users")

    POST_URL_MAP = dict(create="/v1/kllm/users")

    DELETE_URL_MAP = dict(delete="/v1/kllm/users/{user_id}")

    def delete(self, timeout: int = None):
        return self.delete("delete", timeout=timeout)
