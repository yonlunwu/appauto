from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAudioModel:
    def test_audio_model_create_replica(self, amaas: AMaaS):
        assert amaas

        audios = amaas.model.audio
        logger.info(len(audios))

        audio = audios[0]
        worker_id = amaas.workers[0].object_id

        audio.check(worker_id=worker_id, tp=1)
        audio.create_replica(worker_id=worker_id, tp=1)

    def test_audio_model_stop(self, amaas: AMaaS):
        assert amaas

        audios = amaas.model.audio
        logger.info(len(audios))

        audio = audios[0]

        for ins in audio.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        audio.stop()
