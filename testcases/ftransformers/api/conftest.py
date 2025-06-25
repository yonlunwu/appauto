import pytest
import allure


from testcases.ftransformers.conftest import FTCommonCheck as checker


@pytest.fixture(autouse=True, scope="function")
def fixture_assert_server_alive():
    checker.check_sglang_server_alive()
    yield
    checker.check_sglang_server_alive()
