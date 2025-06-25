import pytest
import allure
from itertools import islice
from uuid import uuid4
from typing import Dict, Literal, List, Union
from human_eval.evaluation import evaluate_functional_correctness
from human_eval.data import write_jsonl, read_problems, HUMAN_EVAL

from appauto.manager.config_manager import LoggingConfig

from testcases.ftransformers.correct.conftest import CommonHumanEval as cs, CommonCheck as checker, CommonRunTest as cr

logger = LoggingConfig.get_logger()


# def test_random_demo_1():
#     problem_file = f"./problem_{str(uuid4())}.jsonl"
#     sample_file = f"./sample_{str(uuid4())}.jsonl"
#     problems = cs.choose_problems("random", length=2)
#     cs.write_problem_file(problem_file, problems)

#     for task_id, problem in problems.items():
#         completions = cs.gen_completion(prompt=problem["prompt"])
#         for cpl in completions:
#             sample = dict(task_id=task_id, completion=cpl)
#             cs.write_sample_file(sample, sample_file)

#     res_jsonl = cs.evaluate(sample_file, problem_file=problem_file)
#     checker.check_humaneval_all_pass(res_jsonl)


@allure.epic("TestHumanEvalCorrect")
class TestHumanEvalCorrect:
    @pytest.mark.dev
    def test_single_random_problems(self, check_humaneval_all_pass):
        """单个测试: 随机选择 4 个 humaneval 数据集进行测试"""
        problem_file, sample_file = check_humaneval_all_pass
        problems = cs.choose_problems("random", length=4)
        cr.run_single_test(problems, problem_file, sample_file)

    @pytest.mark.yanlong
    def test_single_spec_problems(self, check_humaneval_all_pass):
        """单个测试: 指定部分 humaneval 数据集进行测试"""
        problem_file, sample_file = check_humaneval_all_pass
        problems = cs.choose_problems("spec", start=22, stop=23)
        cr.run_single_test(problems, problem_file, sample_file)

    @pytest.mark.dev
    def test_concurrency_random_problems(self, check_humaneval_all_pass):
        """并发测试: 随机选择 8 个 humaneval 数据集进行测试, 并发度: 4"""
        problem_file, sample_file = check_humaneval_all_pass
        problems = cs.choose_problems("random", length=8)
        cr.run_concurrency_test(problems, problem_file, sample_file, concurrency=4)

    @pytest.mark.night
    def test_single_all_problems(self, check_humaneval_all_pass):
        """单个测试所有 humaneval 数据集"""
        problem_file, sample_file = check_humaneval_all_pass
        problems = cs.choose_problems("all")
        cr.run_single_test(problems, problem_file, sample_file)

    def test_concurrency_all_problems(self, check_humaneval_all_pass):
        """并发测试所有 humaneval 数据集"""
        problem_file, sample_file = check_humaneval_all_pass
        problems = cs.choose_problems("all")
        cr.run_concurrency_test(problems, problem_file, sample_file, concurrency=4)
