import pytest
import allure

from appauto.manager.config_manager import LoggingConfig

from testcases.ftransformers.correct.human_eval.conftest import (
    CommonHumanEval as cs,
    CommonRunTestHumanEval as cr,
)
from testcases.ftransformers.gen_data import DefaultParams as DP

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


@allure.epic("TestCorrectHumanEval")
class TestCorrectHumanEval:
    # @pytest.mark.dev
    def test_single_random_problems(self, fixture_check_humaneval_all_pass):
        """单并发测试: 随机选择 4 个 humaneval 数据集进行测试"""
        problem_file, sample_file = fixture_check_humaneval_all_pass
        problems = cs.choose_problems("random", length=DP.humaneval_problems_num)
        cr.run_single_test(problems, problem_file, sample_file)

    # @pytest.mark.yanlong
    def test_single_spec_problems(self, fixture_check_humaneval_all_pass):
        """单并发测试: 指定部分 humaneval 数据集进行测试"""
        problem_file, sample_file = fixture_check_humaneval_all_pass
        problems = cs.choose_problems("spec", start=22, stop=23)
        cr.run_single_test(problems, problem_file, sample_file)

    # @pytest.mark.dev
    def test_concurrency_random_problems(self, fixture_check_humaneval_all_pass):
        """多并发测试(默认 8 并发): 随机选择 8 个 humaneval 数据集进行测试, 并发度: 4"""
        problem_file, sample_file = fixture_check_humaneval_all_pass
        problems = cs.choose_problems("random", length=DP.humaneval_problems_num)
        cr.run_concurrency_test(problems, problem_file, sample_file, concurrency=DP.humaneval_concurrency)

    @pytest.mark.night
    def test_single_all_problems(self, fixture_check_humaneval_all_pass):
        """单并发测试所有 humaneval 数据集"""
        problem_file, sample_file = fixture_check_humaneval_all_pass
        problems = cs.choose_problems("all")
        cr.run_single_test(problems, problem_file, sample_file)

    @pytest.mark.night
    def test_concurrency_all_problems(self, fixture_check_humaneval_all_pass):
        """多并发测试(默认 8 并发)所有 humaneval 数据集"""
        problem_file, sample_file = fixture_check_humaneval_all_pass
        problems = cs.choose_problems("all")
        cr.run_concurrency_test(problems, problem_file, sample_file, concurrency=DP.humaneval_concurrency)
