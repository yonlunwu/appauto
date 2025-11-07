import pytest
from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT as c


def pytest_addoption(parser):
    parser.addoption("--AMAAS_IP", action="store", default=c.get("amaas_ip", "192.168.110.4"), help="test amaas ip")
    parser.addoption("--AMAAS_PORT", action="store", default=c.get("amaas_port", "10001"), help="test amaas port")
    parser.addoption("--AMAAS_USER", action="store", default="admin", help="test amaas username")
    parser.addoption("--AMAAS_PASSWD", action="store", default="123456", help="test amaas passwd")


@pytest.fixture(scope="session", autouse=True)
def amaas_ip(request):
    return request.config.getoption("--AMAAS_IP")


@pytest.fixture(scope="session", autouse=True)
def amaas_port(request):
    return request.config.getoption("--AMAAS_PORT")


@pytest.fixture(scope="session", autouse=True)
def amaas_user(request):
    return request.config.getoption("--AMAAS_USER")


@pytest.fixture(scope="session", autouse=True)
def amaas_passwd(request):
    return request.config.getoption("--AMAAS_PASSWD")


@pytest.fixture
def amaas(amaas_ip, amaas_port, amaas_user, amaas_passwd) -> AMaaS:
    return AMaaS(amaas_ip, amaas_port, amaas_user, amaas_passwd)
