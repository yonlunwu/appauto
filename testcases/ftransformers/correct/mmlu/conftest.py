import re
import json
import allure
import random
import pytest
from dataclasses import dataclass
from typing import Dict, List, Literal
import pandas as pd
from functools import partial
from time import time
from datasets import load_dataset
from concurrent.futures import wait
from appauto.manager.utils_manager.custom_thread_pool_executor import (
    CustomThreadPoolExecutor,
    CustomFuture,
)
from appauto.manager.config_manager import LoggingConfig

from testcases.ftransformers.gen_data import sglang, sglang_server, DefaultParams as DP

logger = LoggingConfig.get_logger()


HINT = (
    "There is a single choice question. Answer the question by replying A, B, C, D. "
    "No other answers are accepted. Just the letter."
)


@pytest.fixture
def inner_fixture_data_evaluator():
    data_evaluator = MMLUDataEvaluator()
    data_evaluator.load_data(file_path="cais/mmlu")

    yield data_evaluator


@dataclass
class MMLUResultSummary:
    average_score: float
    total_score: int
    questions_num: int
    total_elapse_time_s: float
    throughput: float
    average_score_2_for_concurrency: int = None
    total_score_2_for_concurrency: int = None
    concurrency: int = None

    def __post_init__(self):
        self.average_score = self.total_score / self.questions_num if self.questions_num else 0

    def __str__(self):
        attributes = [f"{k}={v}" for k, v in self.__dict__.items()]
        class_name = type(self).__name__
        return f"{class_name}({','.join(attributes)})"


class MMLUDataEvaluator:
    def __init__(self):
        self.data: List[Dict] = []

    def load_data(self, file_path):
        """
        Load data from a Parquet file into a list.
        Each record in the Parquet file should represent an individual record.
        """
        # 读取 Parquet 文件
        # dataset = load_dataset('parquet', data_files=file_path)
        ds = load_dataset(file_path, "all")
        df = pd.DataFrame(ds["test"])

        for _, row in df.iterrows():
            self.data.append(row.to_dict())


class CommonMMLU:
    @classmethod
    @allure.step("choose_questions")
    def choose_questions(
        cls, data_evaluator: MMLUDataEvaluator, scope: Literal["all", "random"], count: int = DP.mmlu_questions_num
    ) -> List[Dict]:
        if scope == "all":
            return data_evaluator.data

        elif scope == "random":
            return random.sample(data_evaluator.data, count or DP.mmlu_questions_num)

    @classmethod
    @allure.step("_process_prediction")
    def _process_prediction(cls, prediction: str) -> str:
        prediction = prediction.lstrip("\n").split("\n")[-1]
        return prediction[-1:]

    @classmethod
    @allure.step("gen_prompt")
    def gen_prompt(cls, standard_question: Dict):
        """
        standard_question: mmlu 中每个标准问题
        """
        options_str = "\n".join([f"{chr(65 + i)}. {opt}" for i, opt in enumerate(standard_question["choices"])])
        prompt = HINT + "\nQuestion: " + standard_question["question"] + "\n" + options_str + "\nAnswer: '"
        logger.info(f"prompt: {prompt}")
        return prompt

    @classmethod
    @allure.step("gen_prediction")
    def gen_prediction(cls, prompt):
        res = sglang.talk(prompt, sglang_server.served_model_name, temperature=0.6, stream=False, encode_result=True)
        prediction = res.choices[0].message.content

        assert prediction

        prediction = cls._process_prediction(prediction)
        logger.info(f"get prediction: {prediction}")

        return prediction

    @classmethod
    @allure.step("extract_answer_by_re")
    def extract_answer_by_re(cls, prediction: str):
        """
        提取模型预测的最终选项 (如 A/B/C/D)
        支持自然语言、多行、markdown、高亮、非末尾结论等格式
        """
        prediction = prediction.strip()

        # 1. 显式语句匹配（优先）
        explicit_patterns = [
            r"Answer:\s*([A-D])\b",
            r"Correct answer:\s*([A-D])\b",
            r"The correct answer is\s*\*?\*?\s*([A-D])\b",
            r"Answer is\s*([A-D])\b",
            r"Therefore,\s*answer is\s*([A-D])\b",
            r"Therefore,\s*the answer should be\s*(?:Option\s*)?([A-D])\b",
            r"The answer should be\s*(?:Option\s*)?([A-D])\b",
            r"Option\s+([A-D])\s+is correct",
        ]
        for pat in explicit_patterns:
            match = re.search(pat, prediction, re.IGNORECASE)
            if match:
                res = match.group(1).upper()
                logger.info(f"get prediction: {res}")
                return res

        # 2. markdown 强调 **C**, **C. something**
        markdown_match = re.findall(r"\*\*\s*([A-D])[\.\s]?", prediction)
        if markdown_match:
            res = markdown_match[-1].upper()
            logger.info(f"get prediction: {res}")
            return res

        # 3. 查找单引号中的 'C' 或 "C"
        quote_match = re.findall(r"['\"]([A-D])['\"]", prediction)
        if quote_match:
            res = quote_match[-1].upper()
            logger.info(f"get prediction: {res}")
            return res

        # 4. 倒数几行是否以 "C." 或 "C" 开头
        lines = prediction.splitlines()
        for line in reversed(lines[-5:]):
            line = line.strip()
            match = re.match(r"^([A-D])([.\s]|$)", line)
            if match:
                res = match.group(1).upper()
                logger.info(f"get prediction: {res}")
                return res

        # 再不行就返回 None
        logger.info(f"get prediction: {res}")
        return None

    @classmethod
    @allure.step("score")
    def score(cls, prediction, answers):
        for answer in answers:
            if prediction == answer:
                return 1

        return 0


class CommonCheckMMLU:
    @classmethod
    @allure.step("check_single_passrate_of_mmlu")
    def check_single_passrate_of_mmlu(cls, mmlu_result_summary: MMLUResultSummary):
        assert (
            mmlu_result_summary.average_score >= DP.mmlu_expect_passrate
            and mmlu_result_summary.total_score >= 100 * DP.mmlu_expect_passrate
        )

    @classmethod
    @allure.step("check_concurrency_passrate_of_mmlu")
    def check_concurrency_passrate_of_mmlu(cls, mmlu_result_summary: MMLUResultSummary):
        min_score = min(mmlu_result_summary.total_score, mmlu_result_summary.total_score_2_for_concurrency)
        assert min_score >= 100 * DP.mmlu_expect_passrate


class CommonRunTestMMLU:
    @classmethod
    @allure.step("run_single_test")
    def run_single_test(cls, questions: List[Dict]):
        """
        - 接收 questions 列表;
        - 生成 prompt;
        - 生成答案 (prediction);
        - 与预期答案对比得到分数;
        - 汇总 summary
        - 检查平均得分
        """
        init_start_time = time()
        total_score = 0
        questions_num = len(questions)

        for idx, std_question in enumerate(questions):
            logger.debug(f"question: {std_question}")  # Dict
            prompt = CommonMMLU.gen_prompt(std_question)

            start_time = time()

            try:
                prediction = CommonMMLU.gen_prediction(prompt)
                exp_answer = chr(std_question["answer"] + 65)
                score = CommonMMLU.score(prediction, exp_answer)
                elapse = time() - start_time

                total_score += score

                result = dict(question_id=idx, answer=exp_answer, prediction=prediction, score=score, time=elapse)
                logger.info(f"result: {json.dumps(result)}")

            except Exception as e:
                logger.error(f"error occurred while talking to model: {e}")
                pytest.fail(f"error occurred while talking to model: {e}")

        total_elapse = time() - init_start_time

        result_summary = MMLUResultSummary(
            total_elapse_time_s=total_elapse,
            throughput=questions_num / total_elapse,
            average_score=total_score / questions_num,
            total_score=total_score,
            questions_num=questions_num,
        )
        logger.info(f"final mmlu test result summary: {result_summary}".center(300, "*"))

        CommonCheckMMLU.check_single_passrate_of_mmlu(result_summary)

    @classmethod
    @allure.step("run_concurrency_test")
    def run_concurrency_test(cls, questions: List[Dict]):
        """多并发测试"""

        init_start_time = time()
        total_score, total_score_2 = 0, 0
        questions_num = len(questions)

        def _callback(fu: CustomFuture):
            """处理分数"""
            try:
                nonlocal total_score, total_score_2
                result = fu.result()
                total_score += result["score"]
                total_score_2 += result["score_2"]

            except Exception as e:
                logger.error(f"error occurred while talking to model: {e}")
                raise e

        def _worker(idx: int, std_question: Dict):
            logger.debug(f"question: {std_question}")  # Dict
            prompt = CommonMMLU.gen_prompt(std_question)
            start_time = time()

            prediction = CommonMMLU.gen_prediction(prompt)
            # 预期答案：将数字转换成字母（0->A, 1->B, 2->C, 3->D）
            exp_answer = chr(std_question["answer"] + 65)
            # 多并发中可能有格式问题, 先用 gen_prediction 提取 answer 计算一次分数
            score = CommonMMLU.score(prediction, exp_answer)
            # 再用 extract_answer_by_re 提取 answer 重新计算一次分数
            score_2 = CommonMMLU.score(CommonMMLU.extract_answer_by_re(prediction), exp_answer)
            elapse = time() - start_time

            result = dict(
                question_id=idx, answer=exp_answer, prediction=prediction, score=score, score_2=score_2, time=elapse
            )
            logger.info(f"result: {json.dumps(result)}")

            return result

        try:
            with CustomThreadPoolExecutor(max_workers=DP.mmlu_concurrency) as executor:
                fus = []
                for idx, qst in enumerate(questions):
                    fu = executor.submit(_worker, idx, qst)
                    fu.add_done_callback(partial(_callback))
                    fus.append(fu)

                wait(fus)

        finally:
            total_elapse = time() - init_start_time
            result_summary = MMLUResultSummary(
                total_elapse_time_s=total_elapse,
                throughput=questions_num / total_elapse,
                average_score=total_score / questions_num if questions_num else 0,
                total_score=total_score,
                questions_num=questions_num,
                total_score_2_for_concurrency=total_score_2,
                average_score_2_for_concurrency=total_score_2 / questions_num if questions_num else 0,
                concurrency=DP.mmlu_concurrency,
            )
            logger.info(f"final mmlu test result summary: {result_summary}".center(300, "*"))

            CommonCheckMMLU.check_single_passrate_of_mmlu(mmlu_result_summary=result_summary)
