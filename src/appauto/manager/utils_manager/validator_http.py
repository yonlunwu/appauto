# appauto/utils/validator.py

from addict import Dict as ADDict
from httpx import Response
import jmespath
from typing import Any, Dict, List
from appauto.manager.config_manager import LoggingConfig
import re

logger = LoggingConfig.get_logger()


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


def to_dict(resp: Response) -> ADDict:
    """将 httpx.Response 转为 ADDict，便于链式访问"""
    try:
        return ADDict(resp.json())
    except Exception:
        return ADDict({"raw": resp.text})


class ResponseValidator:
    def __init__(self, response: Response):
        self.response = response
        self.data = to_dict(response)
        self.errors: List[str] = []

    def validate(self, schema: Dict[str, Any]) -> bool:
        """
        验证响应是否符合预期
        schema 示例：
        {
            "status_code": 200,  # 验证 HTTP 状态码
            "rc": 200,          # 验证响应中的 rc 字段
            "has_fields": ["data.user", "data.enabled"],  # 验证字段存在
            "not_has_fields": ["data.error"],  # 验证字段不存在
            "type_check": {     # 类型检查
                "data.user": "string",
                "data.age": "number"
            },
            "equals": {         # 精确匹配
                "data.user.name": "admin",
                "data.enabled": True
            },
            "contains": {       # 包含关系
                "data.tags": ["tag1", "tag2"]
            },
            "greater_than": {   # 大于
                "data.age": 18
            },
            "less_than": {      # 小于
                "data.score": 100
            },
            "regex": {          # 正则匹配
                "data.email": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            }
        }
        """
        try:
            self._validate_status_code(schema)
            self._validate_rc(schema)
            self._validate_has_fields(schema)
            self._validate_not_has_fields(schema)
            self._validate_type_check(schema)
            self._validate_equals(schema)
            self._validate_contains(schema)
            self._validate_greater_than(schema)
            self._validate_less_than(schema)
            self._validate_regex(schema)

            if self.errors:
                raise ValidationError("\n".join(self.errors))
            return True
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise

    def _validate_status_code(self, schema: Dict[str, Any]):
        if "status_code" in schema:
            expected = schema["status_code"]
            actual = self.response.status_code
            if actual != expected:
                self.errors.append(f"Status code mismatch: expected {expected}, got {actual}")

    def _validate_rc(self, schema: Dict[str, Any]):
        if "rc" in schema:
            expected = schema["rc"]
            actual = self.data.get("rc")
            if actual != expected:
                self.errors.append(f"RC mismatch: expected {expected}, got {actual}")

    def _validate_has_fields(self, schema: Dict[str, Any]):
        for field in schema.get("has_fields", []):
            value = jmespath.search(field, self.data)
            if value is None:
                self.errors.append(f"Required field '{field}' is missing")

    def _validate_not_has_fields(self, schema: Dict[str, Any]):
        for field in schema.get("not_has_fields", []):
            value = jmespath.search(field, self.data)
            if value is not None:
                self.errors.append(f"Field '{field}' should not exist")

    def _validate_type_check(self, schema: Dict[str, Any]):
        type_map = {"string": str, "number": (int, float), "boolean": bool, "array": list, "object": dict}

        for field, expected_type in schema.get("type_check", {}).items():
            value = jmespath.search(field, self.data)
            if value is None:
                self.errors.append(f"Field '{field}' is missing for type check")
                continue

            if expected_type not in type_map:
                self.errors.append(f"Unknown type '{expected_type}' for field '{field}'")
                continue

            if not isinstance(value, type_map[expected_type]):
                self.errors.append(f"Type mismatch for '{field}': expected {expected_type}, got {type(value).__name__}")

    def _validate_equals(self, schema: Dict[str, Any]):
        for field, expected in schema.get("equals", {}).items():
            actual = jmespath.search(field, self.data)
            if actual != expected:
                self.errors.append(f"Field '{field}': expected {expected}, got {actual}")

    def _validate_contains(self, schema: Dict[str, Any]):
        for field, expected_items in schema.get("contains", {}).items():
            actual = jmespath.search(field, self.data)
            if not isinstance(actual, list):
                self.errors.append(f"Field '{field}' is not a list")
                continue

            for item in expected_items:
                if item not in actual:
                    self.errors.append(f"Field '{field}' does not contain {item}")

    def _validate_greater_than(self, schema: Dict[str, Any]):
        for field, expected in schema.get("greater_than", {}).items():
            actual = jmespath.search(field, self.data)
            if not isinstance(actual, (int, float)):
                self.errors.append(f"Field '{field}' is not a number")
                continue

            if actual <= expected:
                self.errors.append(f"Field '{field}': expected > {expected}, got {actual}")

    def _validate_less_than(self, schema: Dict[str, Any]):
        for field, expected in schema.get("less_than", {}).items():
            actual = jmespath.search(field, self.data)
            if not isinstance(actual, (int, float)):
                self.errors.append(f"Field '{field}' is not a number")
                continue

            if actual >= expected:
                self.errors.append(f"Field '{field}': expected < {expected}, got {actual}")

    def _validate_regex(self, schema: Dict[str, Any]):
        for field, pattern in schema.get("regex", {}).items():
            actual = jmespath.search(field, self.data)
            if not isinstance(actual, str):
                self.errors.append(f"Field '{field}' is not a string")
                continue

            if not re.match(pattern, actual):
                self.errors.append(f"Field '{field}' does not match pattern '{pattern}'")


def validate_response(response: Response, schema: Dict[str, Any]) -> bool:
    """
    验证响应的便捷函数
    """
    validator = ResponseValidator(response)
    return validator.validate(schema)
