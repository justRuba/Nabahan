# evaluation/eval_suite.py
# Nabahan Evaluation Pipeline
# Scores on Answer Relevancy and Faithfulness
# Saves to logs/eval_results.csv (Backend Only - Never shown to users)

import csv
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.nabahan_logic import nabahan_agent
from agent.config import EVAL_LOG_PATH


class NabahanEvaluator:
    """
    Evaluation pipeline for Nabahan agent.
    Tests Answer Relevancy and Faithfulness using rule-based metrics.
    Results are saved to CSV - never exposed to frontend.
    """

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or EVAL_LOG_PATH
        log_dir = Path(self.log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize CSV with headers if new
        if not os.path.exists(self.log_path):
            self._init_csv()

    def _init_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            'timestamp', 'question', 'status', 'sql', 'data_rows',
            'insights', 'relevancy_score', 'faithfulness_score',
            'relevancy_passed', 'faithfulness_passed', 'overall_passed'
        ]
        with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def evaluate_relevancy(self, question: str, answer: str, data_rows: int) -> Dict[str, Any]:
        """
        Evaluate answer relevancy using rule-based approach.
        Score 0-1 based on:
        - Answer not empty
        - Answer in Arabic
        - Contains relevant numbers
        - Keyword overlap with question
        """
        score = 0.0
        reasons = []

        # Answer not empty
        if answer and len(answer) > 10:
            score += 0.25
            reasons.append("Non-empty answer")

        # Arabic content
        if any('\u0600' <= c <= '\u06FF' for c in answer):
            score += 0.25
            reasons.append("Arabic content")

        # Numbers if data exists
        if data_rows > 0:
            numbers = re.findall(r'\d+', answer)
            if numbers:
                score += 0.25
                reasons.append("Contains numbers")
            else:
                score += 0.1
        else:
            if "عذرا" in answer or "غير متوفرة" in answer:
                score += 0.25
                reasons.append("Correct no-data response")

        # Keyword overlap
        q_words = set(question.split())
        a_words = set(answer.split())
        overlap = len(q_words.intersection(a_words))
        if overlap >= 2:
            score += 0.25
            reasons.append(f"Keyword overlap: {overlap}")

        return {
            "score": min(score, 1.0),
            "reason": "; ".join(reasons),
            "passed": score >= 0.6
        }

    def evaluate_faithfulness(self, answer: str, sql: str, data_rows: int, status: str) -> Dict[str, Any]:
        """
        Evaluate faithfulness - does answer match the data?
        """
        score = 0.0
        reasons = []

        # Answer matches status
        if status == "success" and data_rows > 0:
            if len(answer) > 30 and "عذرا" not in answer:
                score += 0.4
                reasons.append("Substantive answer for success")
        elif status in ["no_data", "out_of_scope", "error"]:
            if "عذرا" in answer or "غير متوفرة" in answer:
                score += 0.5
                reasons.append("Correct no-data indication")

        # Valid SQL
        if sql and "SELECT" in sql.upper():
            score += 0.3
            reasons.append("Valid SQL")

        # Numbers consistency
        if data_rows > 0 and any(c.isdigit() for c in answer):
            score += 0.3
            reasons.append("Numbers in answer")
        elif data_rows == 0:
            score += 0.2

        return {
            "score": min(score, 1.0),
            "reason": "; ".join(reasons),
            "passed": score >= 0.6
        }

    def run_evaluation(self, question: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Run evaluation on a single question."""
        timestamp = datetime.now().isoformat()

        # Get agent response
        result = nabahan_agent(question, filters)
        data_rows = len(result['data']) if not result['data'].empty else 0

        # Evaluate
        relevancy = self.evaluate_relevancy(question, result['insights'], data_rows)
        faithfulness = self.evaluate_faithfulness(
            result['insights'], result['sql'], data_rows, result['status']
        )

        overall_passed = relevancy['passed'] and faithfulness['passed']

        # Log to CSV
        row = [
            timestamp,
            question,
            result['status'],
            result['sql'][:200] if result['sql'] else '',
            data_rows,
            result['insights'][:300],
            f"{relevancy['score']:.2f}",
            f"{faithfulness['score']:.2f}",
            relevancy['passed'],
            faithfulness['passed'],
            overall_passed
        ]

        with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return {
            "question": question,
            "status": result['status'],
            "relevancy_score": relevancy['score'],
            "faithfulness_score": faithfulness['score'],
            "overall_passed": overall_passed
        }

    def run_test_suite(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """Run evaluation on multiple test cases."""
        print("=" * 60)
        print("Nabahan Evaluation Suite")
        print(f"Log file: {self.log_path}")
        print("=" * 60)

        results = []
        passed = 0

        for i, tc in enumerate(test_cases, 1):
            question = tc.get('question', '')
            filters = tc.get('filters')

            print(f"\n[{i}/{len(test_cases)}] {question[:40]}...")

            result = self.run_evaluation(question, filters)
            results.append(result)

            if result['overall_passed']:
                passed += 1
                print(f"  PASSED (R:{result['relevancy_score']:.2f}, F:{result['faithfulness_score']:.2f})")
            else:
                print(f"  FAILED (R:{result['relevancy_score']:.2f}, F:{result['faithfulness_score']:.2f})")

        # Summary
        summary = {
            "total": len(test_cases),
            "passed": passed,
            "failed": len(test_cases) - passed,
            "pass_rate": passed / len(test_cases) if test_cases else 0,
            "avg_relevancy": sum(r['relevancy_score'] for r in results) / len(results) if results else 0,
            "avg_faithfulness": sum(r['faithfulness_score'] for r in results) / len(results) if results else 0
        }

        print("\n" + "=" * 60)
        print(f"SUMMARY: {passed}/{len(test_cases)} passed ({summary['pass_rate']*100:.1f}%)")
        print(f"Avg Relevancy: {summary['avg_relevancy']:.2f}")
        print(f"Avg Faithfulness: {summary['avg_faithfulness']:.2f}")
        print("=" * 60)

        return summary


def get_default_test_cases() -> List[Dict]:
    """Default test cases for evaluation."""
    return [
        {"question": "كم عدد المناقصات الحالية؟"},
        {"question": "كم عدد المشاريع المستقبلية؟"},
        {"question": "المناقصات في منطقة الرياض"},
        {"question": "اكثر الجهات الحكومية مناقصات"},
        {"question": "توزيع المناقصات حسب الحالة"},
        {"question": "ما هي المناطق السعودية؟"},
        {"question": "المناقصات المجانية"},
        {"question": "اعلى 5 جهات من حيث المشاريع"},
        {"question": "ما هو الطقس اليوم؟"},  # Out of scope
        {"question": "اخبرني عن اسعار العقارات"}  # Out of scope
    ]


def main():
    """Run evaluation suite."""
    import argparse

    parser = argparse.ArgumentParser(description='Nabahan Evaluation')
    parser.add_argument('--log-path', type=str, default=None)
    args = parser.parse_args()

    evaluator = NabahanEvaluator(log_path=args.log_path)
    test_cases = get_default_test_cases()
    evaluator.run_test_suite(test_cases)


if __name__ == "__main__":
    main()
