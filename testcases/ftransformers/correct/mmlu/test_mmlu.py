"""
# mmlu 中每个问题的标准结构
{
    "question": " The numen of Augustus referred to which of the following characteristics?",
    "subject": "world_religions",
    "choices": [
        "Divine power",
        "Sexual virility",
        "Military acumen",
        "Philosophical intellect"
    ],
    "answer": 0
}
"""

import pytest
import allure

from testcases.ftransformers.correct.mmlu.conftest import CommonMMLU as cs, CommonRunTestMMLU as cr
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


@allure.epic("TestCorrectMMLU")
class TestCorrectMMLU:
    def test_single_random_peoblems(self, inner_fixture_data_evaluator):
        data_evaluator = inner_fixture_data_evaluator
        questions = cs.choose_questions(data_evaluator, "random")
        cr.run_single_test(questions)

    def test_concurrency_random_problems(self, inner_fixture_data_evaluator):
        data_evaluator = inner_fixture_data_evaluator
        questions = cs.choose_questions(data_evaluator, "random")
        cr.run_concurrency_test(questions)
