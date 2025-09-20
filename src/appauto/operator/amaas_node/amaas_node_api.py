from appauto.manager.component_manager.components.amaas import AMaaS


class AMaaSNodeApi(AMaaS):
    def __init__(
        self,
        mgt_ip=None,
        port=None,
        username="admin",
        passwd="123456",
        object_id=None,
        data=None,
        ssl_enabled=False,
        parent_tokens=None,
        amaas=None,
    ):
        super().__init__(mgt_ip, port, username, passwd, object_id, data, ssl_enabled, parent_tokens, amaas)
