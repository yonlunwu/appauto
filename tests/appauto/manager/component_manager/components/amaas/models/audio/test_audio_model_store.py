from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAudioModelStorage:
    def test_audio_model_storage_check(self, amaas: AMaaS):
        assert amaas

        audio_stores = amaas.init_model_store.audio
        logger.info(len(audio_stores))

        audio = audio_stores[0]
        worker_id = amaas.workers[0].object_id

        audio.check(worker_id=worker_id, tp=1)
        audio.run(worker_id=worker_id, tp=1)
