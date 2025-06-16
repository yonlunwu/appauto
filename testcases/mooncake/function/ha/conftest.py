import pytest
from testcases.mooncake.function.ha.gen_data import mooncake


@pytest.fixture(autouse=True)
def start_server():
    print(mooncake)
