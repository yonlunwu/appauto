from ..base_component import BaseComponent

from pathlib import Path
from typing import Dict


class License(BaseComponent):
    OBJECT_TOKEN = "license_id"

    POST_URL_MAP = dict(upload="/auth/license")
    GET_URL_MAP = dict(get_self="/auth/license")

    def upload(self, license_file: str, timeout: int = None):
        with open(license_file, "rb") as f:
            file_path = Path(license_file)
            files = {"license_file": (file_path.name, f, "application/octet-stream")}
            return self.post("upload", files=files, timeout=timeout)

    @property
    def status(self) -> bool:
        return self.data.license_status

    @property
    def license_info(self) -> Dict:
        return self.data.license_info

    @property
    def device_info(self) -> Dict:
        return self.data.device_info
