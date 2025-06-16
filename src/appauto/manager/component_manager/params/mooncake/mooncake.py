from dataclasses import dataclass
from typing import Literal


@dataclass
class MooncakeClientParams:
    protocol: Literal["tcp", "rdma"] = "tcp"
    device_name: str = None
    local_hostname: str = "localhost"
    metadata_server: str = "http://127.0.0.1:8080/metadata"
    master_server: str = "127.0.0.1:50051"
