"""
基于 ft container 做测试, name 固定为 zhiwen-ft
"""

import threading
from queue import Queue
from typing import TYPE_CHECKING, Literal, Dict, Tuple
from appauto.manager.client_manager import BaseDockerContainer
from appauto.organizer.constructor import ModelParams
from appauto.manager.config_manager.config_logging import LoggingConfig
import time

logger = LoggingConfig.get_logger()

if TYPE_CHECKING:
    from ..amaas_node_cli import AMaaSNodeCli


class FTContainer(BaseDockerContainer):
    def __init__(
        self,
        node: "AMaaSNodeCli",
        name: str = "zhiwen-ft",
        conda_path="/root/miniforge3/bin/conda",
        conda_env="ftransformers",
    ):
        super().__init__(node, name)
        self.conda_path = conda_path
        self.conda_env = conda_env

        # 管理线程与模型状态
        self.threads: Dict[int, threading.Thread] = {}
        self.stop_flags: Dict[int, threading.Event] = {}
        self.model_thread_map: Dict[str, int] = {}

    # TODO 待测试
    def launch_model(
        self,
        model_name: str,
        tp: int,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        sudo=False,
    ):
        """
        阻塞方式启动模型（SSH 远程执行）
        """
        model_params = ModelParams(self.node, engine="ft", model_name=model_name, tp=tp, mode=mode)
        cmd = f"source /root/miniforge3/etc/profile.d/conda.sh && conda activate {self.conda_env} && {model_params.as_cmd}"

        logger.info(f"[FT] launching model in SSH: {cmd}")
        rc, res, err = self.run(cmd, sudo=sudo)

        return rc, res, err

    # TODO 可能是不对的，也可能不用这么麻烦
    def launch_model_in_thread(
        self,
        model_name: str,
        tp: int,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        sudo=False,
    ) -> Tuple[Queue, threading.Thread]:
        """
        在线程中启动远程模型（异步执行）
        返回 (Queue, Thread)
        """
        if model_name in self.model_thread_map:
            th_id = self.model_thread_map[model_name]
            logger.warning(f"模型 {model_name} 已在运行 (线程ID: {th_id})")
            return None, self.threads.get(th_id)

        stop_flag = threading.Event()
        result_q = Queue()

        def _thread(q: Queue, stop_flag: threading.Event):
            th_id = threading.get_ident()
            logger.info(f"[FT] Thread {th_id} started for model {model_name}")

            try:
                model_params = ModelParams(self.node, engine="ft", model_name=model_name, tp=tp, mode=mode)
                cmd = f"conda activate {self.conda_env} && {model_params.as_cmd}"
                logger.info(f"[FT] launching model via SSH: {cmd}")

                # 在远程机器上后台启动模型
                # 例如 nohup + 重定向防止 ssh 阻塞
                background_cmd = f"nohup {cmd} > /tmp/{model_name}.log 2>&1 & echo $!"
                _, pid_str, _ = self.run(background_cmd, sudo=sudo)

                pid = pid_str.strip()
                logger.info(f"[FT] Model {model_name} started with PID {pid}")

                # 轮询检查 stop_flag
                while not stop_flag.is_set():
                    time.sleep(2)
                    # 检查远程进程是否还在运行
                    check_cmd = f"ps -p {pid} > /dev/null"
                    rc_check, _, _ = self.run(check_cmd, sudo=sudo)
                    if rc_check != 0:
                        raise RuntimeError(f"模型 {model_name} 进程意外退出 (pid={pid})")

                # stop_flag 被触发 => 停止模型
                logger.info(f"[FT] Stopping model {model_name} (pid={pid}) ...")
                kill_cmd = f"kill {pid}"
                self.run(kill_cmd, sudo=True)
                q.put((th_id, 0, f"Model {model_name} stopped", ""))

            except Exception as e:
                logger.error(f"[FT] Thread {th_id} error for model {model_name}: {e}")
                q.put((th_id, -1, "", str(e)))

        th = threading.Thread(target=_thread, args=(result_q, stop_flag), daemon=True)
        th.start()

        th_id = th.ident
        self.threads[th_id] = th
        self.stop_flags[th_id] = stop_flag
        self.model_thread_map[model_name] = th_id

        logger.info(f"[FT] Started background thread {th_id} for model {model_name}")
        return result_q, th

    def stop_model_by_name(self, model_name: str) -> bool:
        """
        主动停止指定模型
        """
        if model_name not in self.model_thread_map:
            logger.warning(f"[FT] 模型 {model_name} 不在运行")
            return False

        th_id = self.model_thread_map[model_name]
        stop_flag = self.stop_flags.get(th_id)
        thread = self.threads.get(th_id)

        if not stop_flag or not thread:
            logger.warning(f"[FT] 模型 {model_name} 的线程或 stop_flag 不存在")
            return False

        # 通知线程停止
        stop_flag.set()
        logger.info(f"[FT] Stop signal sent to model {model_name} (thread {th_id})")

        # 等待线程结束
        thread.join(timeout=10)
        if thread.is_alive():
            logger.warning(f"[FT] 模型 {model_name} 的线程未在 10 秒内结束")
        else:
            logger.info(f"[FT] 模型 {model_name} 已成功停止")

        # 清理状态
        self.model_thread_map.pop(model_name, None)
        self.threads.pop(th_id, None)
        self.stop_flags.pop(th_id, None)
        return True
