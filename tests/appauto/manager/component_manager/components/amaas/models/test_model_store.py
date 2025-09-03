from random import choice

from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSModelStore:
    def test_llm_model_store(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci

        failed = []
        for llm in amaas.init_model_store.llm:
            for tp in [1, 2, 4, 8]:
                rule = llm.get_run_rule()
                res = llm.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )
                # 检查通过
                """
                {
                    "retcode": 0,
                    "retmsg": [],
                    "data": {
                        "messages": [],
                        "vram_sum": 87595941888,
                        "average_vram": 43797970944
                    }
                }
                """
                # 检查不通过
                """
                {
                    "retcode": 0,
                    "retmsg": [
                        "Resource detection failed."
                    ],
                    "data": {
                        "messages": [
                            "Resource detection failed."
                        ],
                        "vram_sum": 0,
                        "average_vram": 0
                    }
                }
                """
                if res.data.messages:
                    failed.append({llm.name: tp})

                llm.run(
                    choice(amaas.workers).object_id,
                    # choice([1, 2, 4, 8]),
                    1,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )

        assert not failed

    def test_vlm_model_store(self, amaas: AMaaS):
        failed = []
        for vlm in amaas.init_model_store.vlm:
            for tp in [1, 2, 4, 8]:
                rule = vlm.get_run_rule()
                res = vlm.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )
                if res.data.messages:
                    failed.append({vlm.name: tp})

                vlm.run(
                    choice(amaas.workers).object_id,
                    # choice([1, 2, 4, 8]),
                    1,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )

        assert not failed

    def test_embedding_model_store(self, amaas: AMaaS):
        failed = []
        for embedding in amaas.init_model_store.embedding:
            for tp in [1, 2, 4, 8]:
                rule = embedding.get_run_rule()
                res = embedding.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )
                if res.data.messages:
                    failed.append({embedding.name: tp})

                embedding.run(
                    choice(amaas.workers).object_id,
                    # choice([1, 2, 4, 8]),
                    1,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )

        assert not failed

    def test_rerank_model_store(self, amaas: AMaaS):
        failed = []
        for rerank in amaas.init_model_store.rerank:
            for tp in [1, 2, 4, 8]:
                rule = rerank.get_run_rule()
                res = rerank.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )
                if res.data.messages:
                    failed.append({rerank.name: tp})

                rerank.run(
                    choice(amaas.workers).object_id,
                    1,
                    access_limit=rule.data.access_limit,
                    max_total_tokens=rule.data.max_total_tokens,
                )

        assert not failed

    def test_parser_model_store(self, amaas: AMaaS):
        failed = []
        for parser in amaas.init_model_store.parser:
            for tp in [1, 2, 4, 8]:
                rule = parser.get_run_rule()
                res = parser.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                )
                if res.data.messages:
                    failed.append({parser.name: tp})

                parser.run(
                    choice(amaas.workers).object_id,
                    # choice([1, 2, 4, 8]),
                    1,
                    access_limit=rule.data.access_limit,
                )

        assert not failed

    def test_audio_model_store(self, amaas: AMaaS):
        failed = []
        for audio in amaas.init_model_store.audio:
            for tp in [1, 2, 4, 8]:
                rule = audio.get_run_rule()
                res = audio.check(
                    choice(amaas.workers).object_id,
                    tp,
                    access_limit=rule.data.access_limit,
                )
                if res.data.messages:
                    failed.append({audio.name: tp})

                audio.run(
                    choice(amaas.workers).object_id,
                    1,
                    access_limit=rule.data.access_limit,
                )

        assert not failed

    def test_wait_for_running_outter(self, amaas: AMaaS):
        # 使用 model.wait_for_running 时最好不要有已经在运行的该 model
        assert not [m for m in amaas.model.llm if m.name == "DeepSeek-R1-0528-GPU-weight"]

        r1 = [m_s for m_s in amaas.init_model_store.llm if m_s.name == "DeepSeek-R1-0528-GPU-weight"][0]

        worker = choice(amaas.workers)
        rule = r1.get_run_rule()

        res = r1.check(
            worker_id=worker.object_id,
            tp=1,
            access_limit=rule.data.access_limit,
            max_total_tokens=rule.data.max_total_tokens,
        )
        assert not res.data.messages

        r1.run(
            worker_id=worker.object_id,
            tp=1,
            access_limit=rule.data.access_limit,
            max_total_tokens=rule.data.max_total_tokens,
        )

        model = [m for m in amaas.model.llm if m.name == "DeepSeek-R1-0528-GPU-weight"][0]
        model.wait_for_running()

    def test_wait_for_running_inner(self, amaas: AMaaS):
        # 使用 model.wait_for_running 时最好不要有已经在运行的该 model
        assert not [m for m in amaas.model.llm if m.name == "DeepSeek-R1-0528-GPU-weight"]

        r1 = [m_s for m_s in amaas.init_model_store.llm if m_s.name == "DeepSeek-R1-0528-GPU-weight"][0]

        worker = choice(amaas.workers)
        rule = r1.get_run_rule()

        res = r1.check(
            worker_id=worker.object_id,
            tp=1,
            access_limit=rule.data.access_limit,
            max_total_tokens=rule.data.max_total_tokens,
        )
        assert not res.data.messages

        model = r1.run(
            worker_id=worker.object_id,
            tp=1,
            access_limit=rule.data.access_limit,
            max_total_tokens=rule.data.max_total_tokens,
            wait_for_running=True,
        )
        logger.info(model.object_id)
        logger.info(model.name)
