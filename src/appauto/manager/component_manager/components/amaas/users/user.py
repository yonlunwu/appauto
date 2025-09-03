from ....base_component import BaseComponent


class AMaaSUser(BaseComponent):
    OBJECT_TOKEN = "user_id"

    GET_URL_MAP = dict(get_self="/v1/kllm/users")

    POST_URL_MAP = dict(create="/v1/kllm/users")

    DELETE_URL_MAP = dict(delete="/v1/kllm/users/{user_id}")

    def refresh(self, alias=None):
        res = super().refresh(alias)
        self.data = [item for item in res.data.get("items") if item.id == self.object_id][0]
        return res

    def delete(self, timeout: int = None):
        return self.delete("delete", timeout=timeout)
