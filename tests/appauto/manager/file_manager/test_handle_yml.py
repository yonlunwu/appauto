import pytest
from appauto.manager.file_manager.handle_yml import HandleYML


yml_path = "tests/appauto/manager/file_manager/test_yml.yml"


@pytest.mark.ci
class TestHandleYml:
    def test_load_yml(self):
        config = HandleYML(yml_path)
        assert config.data
        assert config.data.ip == "1.1.1.1"
        assert config.data.yanlong.data
        assert config.data.yanlong.data[0].Ruby == "ruby-lang.org"
        assert isinstance(config.data.yanlong.data[-1]["C++"], list)

    def test_write_yml(self):
        config = HandleYML(yml_path)
        config.data.ip = "1.1.1.3"
        config.write()
        config = HandleYML("tests/appauto/manager/file_manager/test_yml.yml")
        assert config.data.ip == "1.1.1.3"
        config.data.ip = "1.1.1.1"
        config.write()
        config = HandleYML(yml_path)
        assert config.data.ip == "1.1.1.1"

    def test_as_dict(self):
        config = HandleYML(yml_path)
        assert isinstance(config.as_dict(), dict)
