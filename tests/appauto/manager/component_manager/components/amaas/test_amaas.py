from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaS:
    def test_model_stores(self, amaas: AMaaS):
        assert amaas.llm_model_stores
        assert amaas.vlm_model_stores
        assert amaas.embedding_model_stores
        assert amaas.parser_model_stores
        assert amaas.audio_model_stores

    def test_get_license(self, amaas: AMaaS):
        license = amaas.license()
        logger.info(license.status)
        logger.info(license.license_info)
        logger.info(license.device_info)
        assert license.status is True
        assert isinstance(license.license_info, dict)
        assert isinstance(license.device_info, dict)

    def test_upload_license(self, amaas: AMaaS):
        license = amaas.license()
        logger.info(license.status)
        logger.info(license.license_info)
        logger.info(license.device_info)

        res = license.upload(license_file="../LICENSE.txt")
        logger.info(res)

        license = amaas.license()
        logger.info(license.status)
        logger.info(license.license_info)
        logger.info(license.device_info)
