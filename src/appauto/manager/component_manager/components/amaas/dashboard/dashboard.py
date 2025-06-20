from ....base_component import BaseComponent


class DashBoard(BaseComponent):
    OBJECT_TOKEN = "dashboard_id"

    GET_URL_MAP = dict(get="/v1/kllm/dashboard")

    @property
    def resource_counts(self):
        return self.data.resource_counts

    @property
    def system_load(self):
        return self.data.system_load

    @property
    def model_usage(self):
        return self.data.model_usage

    @property
    def active_models(self):
        return self.data.active_models
