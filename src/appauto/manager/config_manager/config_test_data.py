import os
from pathlib import Path
from typing import Dict
from ..file_manager.handle_ini import HandleIni
from .config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class TestDataConfig:
    """测试数据配置管理类"""

    TEST_DATA_INI = "test_data.ini"

    def __init__(self):
        self.config = HandleIni(Path(self.TEST_DATA_INI))

    @classmethod
    def generate_testdata_ini(cls):
        """生成初始的 test_data.ini 文件"""
        content = """
[data]
repeat = 1
mode = pytest
"""
        with open(cls.TEST_DATA_INI, "w", encoding="utf-8") as file:
            file.write(content.lstrip())

    def reconfig_testdata(self, **kwargs):
        """根据用户配置重新设置 test_data.ini"""
        if not self.config.config.has_section("data"):
            self.config.config.add_section("data")

        # 获取现有配置
        cur_cfg = dict(self.config.config.items("data"))
        logger.info(f"current_config: {cur_cfg}")

        # 需要更新的配置
        updates = {}

        # 检查并更新配置
        for key, value in kwargs.items():
            if key not in cur_cfg or cur_cfg[key] != str(value):
                updates[key] = str(value)

        # 如果有需要更新的配置，则更新
        if updates:
            for key, value in updates.items():
                self.config.config.set("data", key, value)
            self.config.write()
            logger.debug(f"Updated test_data.ini with: {updates}")

    def get_testdata(self) -> Dict[str, str]:
        """获取测试数据配置"""
        return dict(self.config.config.items("data"))

    def config_testdata(self, **kwargs):
        """配置测试数据"""
        self.generate_testdata_ini()
        self.reconfig_testdata(**kwargs)

    def cleanup(self):
        """清理配置文件"""
        if os.path.exists(self.TEST_DATA_INI):
            os.remove(self.TEST_DATA_INI)
            logger.info(f"Removed {self.TEST_DATA_INI}")
