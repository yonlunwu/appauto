from functools import cached_property
from typing import Dict, List, Literal

from appauto.manager.client_manager import BaseLinux
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager.format_output import str_to_list_by_split

from .components.docker_ctn_factory import DockerContainerFactory

logger = LoggingConfig.get_logger()


class AMaaSNodeCli(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)
        self.docker_ctn_factory = DockerContainerFactory(self)

    @cached_property
    def local_models(self) -> Dict[str, Dict]:
        """
        通过 cli 获取节点 /mnt/data/models/ 中有哪些模型
        """
        from appauto.organizer.model_params.constructor.base_model_config import BaseModelConfig

        cmd = "ls /mnt/data/models/ | egrep -v 'AMES|download.sh|perftest'"
        _, res, _ = self.run(cmd)
        res = str_to_list_by_split(res, singleLine=False)
        logger.info(res)
        logger.info(type(res))

        config = BaseModelConfig()
        logger.info(config.model_config)
        logger.info(type(config.model_config))

        return {k: v for k, v in config.model_config.items() if k in res}

    def select_local_models(
        self,
        priority: List[Literal["P0", "P1", "P2", "P3"]] = None,
        model_type: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"] = None,
    ) -> List[str]:
        """
        根据类型和优先级筛选模型, 不填默认返回全部
        """
        models = self.local_models

        if priority:
            models = {name: info for name, info in models.items() if info.get("priority") in priority}

        if model_type:
            models = {name: info for name, info in models.items() if info.get("type") == model_type}

        return models.keys()
