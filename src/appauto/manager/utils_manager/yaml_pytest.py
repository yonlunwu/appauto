import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from appauto.manager.connection_manager.http import HttpClient
from appauto.manager.utils_manager.validator_http import ResponseValidator
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.config_manager.config_test_data import TestDataConfig

logger = LoggingConfig.get_logger()


def pytest_collect_file(parent, path):
    """收集 YAML 测试文件"""
    if path.ext == ".yaml" or path.ext == ".yml":
        return YamlFile.from_parent(parent, path=Path(path))


class YamlFile(pytest.File):
    """表示一个 YAML 测试文件"""

    def collect(self):
        """收集文件中的所有测试用例"""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict) or "TEST_CASE" not in data:
                raise ValueError("YAML file must contain 'TEST_CASE' key")

            for case_data in data["TEST_CASE"]:
                yield YamlItem.from_parent(self, name=case_data["name"], case_data=case_data)
        except Exception as e:
            logger.error(f"Failed to parse YAML file {self.path}: {str(e)}")
            raise


class YamlItem(pytest.Item):
    """表示一个 YAML 测试用例"""

    def __init__(self, name, parent, case_data):
        super().__init__(name, parent)
        self.case_data = case_data
        self.variables: Dict[str, Any] = {}

    def runtest(self):
        """运行测试用例"""
        # 获取测试数据配置
        test_data_config = TestDataConfig()
        config = test_data_config.get_testdata()
        base_url = config.get("base_url")
        headers = config.get("headers", {})
        timeout = int(config.get("timeout", 10))
        verify = config.get("verify", "false").lower() == "true"

        # 创建 HTTP 客户端
        http_client = HttpClient(headers=headers, timeout=timeout, verify=verify)

        try:
            # 运行测试步骤
            for step in self.case_data["steps"]:
                self._run_step(http_client, step, base_url)
        finally:
            http_client.close()

    def _run_step(self, http_client: HttpClient, step: Dict[str, Any], base_url: str):
        """运行单个测试步骤"""
        # 处理请求
        request = self._process_variables(step["request"])
        url = self._build_url(request["url"], base_url)

        # 发送请求
        response = http_client.request(
            method=request["method"],
            url=url,
            json=request.get("json"),
            params=request.get("params"),
            headers=request.get("headers"),
        )

        # 处理响应
        self._extract_variables(response, step["response"])

        # 验证响应
        validator = ResponseValidator(response)
        validator.validate(self._process_variables(step["response"]))

    def _build_url(self, path: str, base_url: str) -> str:
        """构建完整的 URL"""
        if path.startswith(("http://", "https://")):
            return path

        if not path.startswith("/"):
            path = "/" + path

        return f"{base_url.rstrip('/')}{path}"

    def _process_variables(self, data: Any) -> Any:
        """处理变量替换"""
        if isinstance(data, str):
            for var_name, var_value in self.variables.items():
                data = data.replace(f"${{{var_name}}}", str(var_value))
            return data
        elif isinstance(data, dict):
            return {k: self._process_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._process_variables(item) for item in data]
        else:
            return data

    def _extract_variables(self, response: Any, response_schema: Dict[str, Any]):
        """从响应中提取变量"""
        if not isinstance(response_schema, dict):
            return

        for key, value in response_schema.items():
            if isinstance(value, str) and value.startswith("$"):
                var_name = value[1:]
                self.variables[var_name] = response.get(key)


def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption("--base-url", action="store", help="Base URL for API requests")
    parser.addoption("--headers", action="store", type=dict, help="Default headers for API requests")
    parser.addoption("--timeout", action="store", type=int, default=10, help="Timeout for API requests")
    parser.addoption("--verify", action="store", type=bool, default=False, help="Verify SSL certificates")
