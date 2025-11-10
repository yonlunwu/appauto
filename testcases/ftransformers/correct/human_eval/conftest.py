import re
import json
import pytest
import allure
import random
import threading
from uuid import uuid4
from itertools import islice
from typing import Literal, Dict, Union, List
from concurrent.futures import as_completed, wait
from human_eval.evaluation import evaluate_functional_correctness
from human_eval.data import write_jsonl, read_problems, HUMAN_EVAL

from appauto.manager.file_manager import JsonlHandler
from appauto.manager.utils_manager.custom_thread_pool_executor import (
    CustomThreadPoolExecutor,
    check_futures_exception,
)
from appauto.manager.config_manager import LoggingConfig

from testcases.ftransformers.gen_data import sglang, sglang_server, DefaultParams as DP

logger = LoggingConfig.get_logger()


@pytest.fixture(autouse=True, scope="function")
def fixture_check_humaneval_all_pass():
    uid = str(uuid4())
    problem_file = f"./problem_{uid}.jsonl"
    sample_file = f"./sample_{uid}.jsonl"

    yield problem_file, sample_file


class CommonHumanEval:
    @classmethod
    @allure.step("choose_problems")
    def choose_problems(
        cls, scope: Literal["all", "random", "spec"] = "all", length: int = None, start=None, stop=None, step=None
    ) -> Dict[str, Dict]:
        """
        挑选要测试的 problems, eg:
            problems = choose_problems('all') # 测试所有问题
            problems = choose_problems("random", length=2) # 随机测试 2 个问题
            problems = choose_problems(scope='spec', length=2) # 测试前两问题
            problems = choose_problems(scope="spec", start=73, stop=75) # 测试第 73-74 这两个问题

        """
        all_problems = read_problems()

        if scope == "all":
            return all_problems

        elif scope == "random":
            if not length:
                return all_problems

            task_ids = random.sample(list(all_problems.keys()), length)

        elif scope == "spec":
            if length:
                task_ids = list(islice(all_problems.keys(), length))
            else:
                task_ids = list(islice(all_problems.keys(), start, stop, step))

        if task_ids:
            problems = {t_id: all_problems[t_id] for t_id in task_ids}

            return problems

        return all_problems

    @classmethod
    @allure.step("write_problem_file")
    def write_problem_file(cls, problem_file: str, problems: Dict[str, Dict]):
        """
        problems: 挑选的 problems
        problem_file: 将挑选的 problem 保存至 problem_file
        """
        for _, value in problems.items():
            write_jsonl(problem_file, [value], append=True)

    @classmethod
    @allure.step("construct_prompt")
    def construct_prompt(cls, prompt: str) -> str:
        return (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n"
            "Complete the following Python code without any tests or explanation, "
            "Emphasize again: Don't test or explanation, Just complete the python code.\n"  # TODO 合理吗？
            f"{prompt}\n\n"
            "### Response:"
        )

    @classmethod
    @allure.step("filter_code")
    def filter_code(cls, completion: str) -> str:
        # ignore think
        completion = completion.split("think>")[-1]
        completion = completion.split("</think>")[-1]
        completion = completion.split("<think/>")[-1]
        completion = completion.split("</>")[-1]
        # The program tends to overwrite, we only take the first function
        completion = completion.lstrip("\n")
        # we also remove ```python\n and ```
        completion = completion.replace("```python\n", "").replace("```", "")
        if 'if __name__ == "__main__":' in completion:
            completion = completion.split('if __name__ == "__main__":')[0]
        if "# Example usage" in completion:
            completion = completion.split("# Example usage")[0]

        # 检查是否还有多余的
        # 如果以 import 或 from 或 def 开头
        if completion.startswith("import") or completion.startswith("from") or completion.startswith("def"):
            logger.info("confirmd that startwith [import|from|def], return")
            return completion

        # TODO 如果以 from 开头, 需要检查是否为 python 关键字
        # TODO 补充 from 的逻辑(是否需要 prompt 约束 import 和 from 的先后顺序？)
        # 查找第一个 'import' ｜ 'from'｜ 'def'
        import_match = re.search(r"^\s*import\s+\S+", completion)
        from_match = re.search(r"^\s*from\s+\S+", completion)
        def_match = re.search(r"^\s*def\s+\S+", completion)

        # 如果找到了 'import'，以 'import' 为准
        if import_match:
            split_index = import_match.start()
        elif from_match:
            split_index = from_match.start()
        elif def_match:
            split_index = def_match.start()
        else:
            logger.info("filter code failed, return init completion")
            return completion  # 如果都没有找到，返回原文本

        # 返回拆分后的文本
        return completion[split_index:]

    @classmethod
    @allure.step("fix_indents")
    def fix_indents(cls, text: str) -> str:
        return text.replace("\t", "    ")

    @classmethod
    @allure.step("gen_completion")
    def gen_completion(cls, prompt) -> List[str]:
        """发送请求并返回 completion
        - problems: 挑选出来的 problems
        - task_id: problem 的 task_id
        """
        prompt = cls.construct_prompt(prompt)
        # TODO temperature 要写死吗？
        # stream 最好不要修改, 因为内部涉及内容的解析
        res = sglang.talk(prompt, sglang_server.served_model_name, temperature=0.6, stream=False, encode_result=True)
        res = cls.filter_code(cls.fix_indents(res.choices[0].message.content))
        logger.info(f"filter code done: {res}")

        return [res]

    @classmethod
    @allure.step("construct_sample")
    def construct_sample(cls, task_id: str, completion) -> Dict:
        return {"task_id": task_id, "completion": completion}

    @classmethod
    @allure.step("write_sample_file")
    def write_sample_file(cls, sample: Union[Dict, List[Dict]], sample_file: str):
        sample = sample if isinstance(sample, list) else [sample]
        write_jsonl(sample_file, sample, append=True)

    @classmethod
    @allure.step("evaluate")
    def evaluate(
        cls,
        sample_file: str,
        k: List[int] = [1, 10, 100],
        n_workers: int = 4,
        timeout: float = 3,
        problem_file: str = HUMAN_EVAL,
        ignore_incomplete: bool = False,
    ) -> str:
        """
        通过 evaluate_functional_correctness 得到 f"{sample_file}_results.jsonl"
        """
        evaluate_functional_correctness(sample_file, k, n_workers, timeout, problem_file, ignore_incomplete)
        res_file = f"{sample_file}_results.jsonl"

        # TODO 校验 res_file 存在
        return res_file


class CommonCheckHumanEval:
    @classmethod
    @allure.step("check_passrate_of_humaneval")
    def check_passrate_of_humaneval(cls, res_jsonl_path: str, problems: Dict[str, Dict]) -> List[str]:
        """检查 humaneval JSONL 文件中通过率 (passed == True and result == 'passed')"""
        passed_ids, failed_ids = [], []

        try:
            jsonl = JsonlHandler(res_jsonl_path)
            for idx, inner_dict in enumerate(jsonl.data):
                if inner_dict and isinstance(inner_dict, dict):
                    if inner_dict.result != "passed" or inner_dict.passed is not True:
                        failed_ids.append(inner_dict.task_id)
                    else:
                        passed_ids.append(inner_dict.task_id)
                else:
                    failed_ids.append(f"unknown_result_of_index_{idx}")

            total = len(problems)
            failed = len(failed_ids)
            passwd = len(passed_ids)
            pass_rate = len(passed_ids) / len(problems)

            logger.warning(f"failed task_ids: {failed_ids}")
            logger.warning(
                f"total problems: {total}: total_failed: {failed}, "
                f"total_passed: {passwd}, pass_rate: {pass_rate}".center(200, "*")
            )

            assert pass_rate >= DP.humaneval_expect_passrate

        except Exception as e:
            msg = f"error occurred in get_failed_task_ids: {e}, failed_ids: {failed_ids}"
            logger.error(msg)
            pytest.fail(reason=msg)


class CommonRunTestHumanEval:
    lock = threading.Lock()

    @classmethod
    @allure.step("run_single_test")
    def run_single_test(cls, problems: Dict[str, Dict], problem_file: str, sample_file: str):
        """
        - write_problem_file: 将 problems 写入 problem_file.jsonl
        - send_request: 发送请求并生成 completion
        - construct_sample: 将 completion 传入 sample
        - write_samples_file: 并将 sample 依次写入 sample-file
        - check_passrate_of_humaneval: 计算通过率
        """
        CommonHumanEval.write_problem_file(problem_file, problems)

        for task_id, problem in problems.items():
            completions = CommonHumanEval.gen_completion(prompt=problem["prompt"])
            for cpl in completions:
                sample = dict(task_id=task_id, completion=cpl)
                CommonHumanEval.write_sample_file(sample, sample_file)

        # evaluate 生成文件并检查通过率
        res_jsonl = CommonHumanEval.evaluate(sample_file, problem_file=problem_file)
        CommonCheckHumanEval.check_passrate_of_humaneval(res_jsonl, problems)

    @classmethod
    @allure.step("run_concurrency_test")
    def run_concurrency_test(
        cls, problems: Dict[str, Dict], problem_file: str, sample_file: str, concurrency: int = DP.humaneval_concurrency
    ):
        """多并发测试"""
        CommonHumanEval.write_problem_file(problem_file, problems)

        def _worker(task_id: str, problem: Dict):
            completions = CommonHumanEval.gen_completion(prompt=problem["prompt"])
            samples = []
            for cpl in completions:
                sample = dict(task_id=task_id, completion=cpl)
                samples.append(sample)

            with cls.lock:
                for sample in samples:
                    CommonHumanEval.write_sample_file(sample, sample_file)

        try:
            with CustomThreadPoolExecutor(max_workers=concurrency) as executor:
                fus = [executor.submit(_worker, t_id, prob) for t_id, prob in problems.items()]
                wait(fus)

            check_futures_exception(fus)

        finally:
            # evaluate 生成文件并检查通过率
            res_jsonl = CommonHumanEval.evaluate(sample_file, problem_file=problem_file)
            CommonCheckHumanEval.check_passrate_of_humaneval(res_jsonl, problems)
