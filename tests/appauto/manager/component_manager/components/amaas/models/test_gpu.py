from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSWorkerGPU:
    def test_list_worker_gpus(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        workers = amaas.workers
        assert workers

        for worker in workers:
            logger.info(f"{worker.name}".center(100, "*"))
            logger.info(worker.data)
            logger.info(worker.object_id)

            logger.info(worker.gpus)

    def test_list_gpu_model_instance_ids(self, amaas: AMaaS):

        for worker in amaas.workers:
            for gpu in worker.gpus:
                logger.info(gpu.name)
                logger.info(gpu)
                logger.info(gpu.object_id)
                logger.info(gpu.data)
                logger.info(gpu.worker)

                logger.info(gpu.model_instances)

                logger.info("llm".center(100, "="))
                logger.info(gpu.model_instances)
                logger.info(gpu.worker.llm_instances_obj)
                if ins_objs := gpu.llm_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)

                logger.info("vlm".center(100, "="))
                if ins_objs := gpu.vlm_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)

                logger.info("embedding".center(100, "="))
                if ins_objs := gpu.embedding_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)

                logger.info("rerank".center(100, "="))
                if ins_objs := gpu.rerank_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)

                logger.info("parser".center(100, "="))
                if ins_objs := gpu.parser_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)

                logger.info("audio".center(100, "="))
                if ins_objs := gpu.audio_instances_obj:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)
