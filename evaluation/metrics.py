# evaluation/metrics.py
# Nabahan Agent - Evaluation Metrics
# Measures: Retrieval Accuracy, Generation Fidelity, Latency

import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    name: str
    score: float  # 0.0 to 1.0
    passed: bool
    details: str = ""


@dataclass
class EvaluationResult:
    """Complete evaluation result for a single query."""
    question: str
    timestamp: str
    status: str
    sql_generated: str
    data_rows: int
    insights: str

    # Metrics
    retrieval_accuracy: float  # Did we get the right data? (0 or 1)
    generation_fidelity: float  # Is the answer truthful? (0 or 1)
    latency_seconds: float  # Time taken for query

    # Pass/Fail
    retrieval_passed: bool
    fidelity_passed: bool
    overall_passed: bool

    # Details
    retrieval_details: str = ""
    fidelity_details: str = ""
    category: str = ""
    expected_table: str = ""


class NabahanMetrics:
    """
    Metrics calculator for Nabahan agent evaluation.

    Metrics:
    1. Retrieval Accuracy: Did we query the correct table and get relevant data?
    2. Generation Fidelity: Is the generated insight truthful to the data?
    3. Latency: How long did the query take?
    """

    # Keywords for table detection
    TABLE_KEYWORDS = {
        'tenders_full_details': ['مناقصة', 'مناقصات', 'منافسة', 'منافسات', 'tender'],
        'future_projects': ['مشروع', 'مشاريع', 'project', 'مستقبل'],
        'government_entity': ['جهة', 'جهات', 'حكومية', 'وزارة', 'هيئة'],
        'regions': ['منطقة', 'مناطق', 'region'],
        'tender_statuses': ['حالة', 'حالات', 'status'],
        'tender_types': ['نوع', 'انواع', 'type'],
        'primary_activity': ['نشاط', 'انشطة', 'activity']
    }

    def __init__(self):
        self.results: List[EvaluationResult] = []
        self.start_time: Optional[float] = None

    def start_timer(self):
        """Start timing a query."""
        self.start_time = time.time()

    def stop_timer(self) -> float:
        """Stop timer and return elapsed seconds."""
        if self.start_time is None:
            return 0.0
        elapsed = time.time() - self.start_time
        self.start_time = None
        return elapsed

    def calculate_retrieval_accuracy(
        self,
        question: str,
        sql: str,
        data_rows: int,
        status: str,
        expected_table: Optional[str] = None,
        category: Optional[str] = None
    ) -> MetricResult:
        """
        Calculate Retrieval Accuracy (0 or 1).

        Criteria:
        - For in-scope queries: Did we query the right table and get data?
        - For out-of-scope queries: Did we correctly reject?
        """
        details = []
        score = 0.0

        # Handle out-of-scope correctly
        if category == "out_of_scope":
            if status == "out_of_scope":
                score = 1.0
                details.append("Correctly identified out-of-scope query")
            else:
                score = 0.0
                details.append("Failed to identify out-of-scope query")

            return MetricResult(
                name="retrieval_accuracy",
                score=score,
                passed=score >= 0.5,
                details="; ".join(details)
            )

        # For in-scope queries
        checks_passed = 0
        total_checks = 3

        # Check 1: Valid SQL generated
        if sql and "SELECT" in sql.upper():
            checks_passed += 1
            details.append("Valid SQL generated")
        else:
            details.append("No valid SQL generated")

        # Check 2: Correct table targeted
        if expected_table:
            if expected_table.lower() in sql.lower():
                checks_passed += 1
                details.append(f"Correct table: {expected_table}")
            else:
                details.append(f"Expected table {expected_table} not found in SQL")
        else:
            # Infer expected table from question
            detected_table = self._detect_table_from_question(question)
            if detected_table and detected_table.lower() in sql.lower():
                checks_passed += 1
                details.append(f"Detected table: {detected_table}")
            elif sql:
                checks_passed += 0.5  # Partial credit
                details.append("Table inference uncertain")

        # Check 3: Data retrieved (if expected)
        if status == "success" and data_rows > 0:
            checks_passed += 1
            details.append(f"Retrieved {data_rows} rows")
        elif status == "no_data":
            checks_passed += 0.5  # Query worked but no matching data
            details.append("Query executed but no data matched")
        else:
            details.append("No data retrieved")

        score = checks_passed / total_checks
        # Binary: 1 if >= 0.6, else 0
        binary_score = 1.0 if score >= 0.6 else 0.0

        return MetricResult(
            name="retrieval_accuracy",
            score=binary_score,
            passed=binary_score == 1.0,
            details="; ".join(details)
        )

    def calculate_generation_fidelity(
        self,
        question: str,
        insights: str,
        sql: str,
        data_rows: int,
        status: str,
        category: Optional[str] = None
    ) -> MetricResult:
        """
        Calculate Generation Fidelity (0 or 1).

        Criteria:
        - Is the generated text truthful to the retrieved data?
        - Does it avoid hallucination?
        """
        details = []
        checks_passed = 0
        total_checks = 4

        # Handle out-of-scope
        if category == "out_of_scope":
            if "عذرا" in insights or "غير متوفرة" in insights:
                return MetricResult(
                    name="generation_fidelity",
                    score=1.0,
                    passed=True,
                    details="Correct out-of-scope response"
                )
            else:
                return MetricResult(
                    name="generation_fidelity",
                    score=0.0,
                    passed=False,
                    details="Did not provide proper out-of-scope message"
                )

        # Check 1: Response matches status
        if status == "success" and data_rows > 0:
            if len(insights) > 30 and "عذرا" not in insights:
                checks_passed += 1
                details.append("Substantive response for success status")
            else:
                details.append("Insufficient response for success status")
        elif status in ["no_data", "error"]:
            if "عذرا" in insights or "غير متوفرة" in insights or len(insights) < 50:
                checks_passed += 1
                details.append("Appropriate response for no-data/error")
            else:
                details.append("Response too elaborate for no-data status")
        else:
            checks_passed += 0.5

        # Check 2: Arabic language consistency
        arabic_chars = sum(1 for c in insights if '\u0600' <= c <= '\u06FF')
        if arabic_chars > len(insights) * 0.3:
            checks_passed += 1
            details.append("Arabic language used")
        else:
            details.append("Low Arabic content")

        # Check 3: Numbers consistency (if data exists)
        if data_rows > 0:
            numbers_in_insight = re.findall(r'\d+', insights)
            if numbers_in_insight:
                checks_passed += 1
                details.append(f"Contains {len(numbers_in_insight)} numbers")
            else:
                details.append("No numbers in insight despite data")
        else:
            checks_passed += 1  # N/A - give credit
            details.append("No data to verify numbers against")

        # Check 4: No obvious hallucination markers
        hallucination_markers = [
            "اعتقد", "ربما", "قد يكون", "لست متأكد",
            "I think", "maybe", "probably"
        ]
        has_hallucination = any(marker in insights for marker in hallucination_markers)
        if not has_hallucination:
            checks_passed += 1
            details.append("No hallucination markers")
        else:
            details.append("Potential hallucination detected")

        score = checks_passed / total_checks
        binary_score = 1.0 if score >= 0.6 else 0.0

        return MetricResult(
            name="generation_fidelity",
            score=binary_score,
            passed=binary_score == 1.0,
            details="; ".join(details)
        )

    def calculate_latency(self, elapsed_seconds: float) -> MetricResult:
        """
        Calculate latency metric.

        Thresholds:
        - Excellent: < 2s
        - Good: 2-5s
        - Acceptable: 5-10s
        - Poor: > 10s
        """
        if elapsed_seconds < 2.0:
            score = 1.0
            details = f"Excellent: {elapsed_seconds:.2f}s"
        elif elapsed_seconds < 5.0:
            score = 0.8
            details = f"Good: {elapsed_seconds:.2f}s"
        elif elapsed_seconds < 10.0:
            score = 0.5
            details = f"Acceptable: {elapsed_seconds:.2f}s"
        else:
            score = 0.2
            details = f"Poor: {elapsed_seconds:.2f}s"

        return MetricResult(
            name="latency",
            score=score,
            passed=score >= 0.5,
            details=details
        )

    def _detect_table_from_question(self, question: str) -> Optional[str]:
        """Detect which table a question is likely targeting."""
        question_lower = question.lower()

        for table, keywords in self.TABLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return table

        return None

    def evaluate_query(
        self,
        question: str,
        result: Dict[str, Any],
        latency: float,
        expected_table: Optional[str] = None,
        category: Optional[str] = None
    ) -> EvaluationResult:
        """
        Run all metrics on a single query result.
        """
        status = result.get('status', 'error')
        sql = result.get('sql', '')
        insights = result.get('insights', '')
        data = result.get('data')
        data_rows = len(data) if data is not None and not data.empty else 0

        # Calculate metrics
        retrieval = self.calculate_retrieval_accuracy(
            question, sql, data_rows, status, expected_table, category
        )
        fidelity = self.calculate_generation_fidelity(
            question, insights, sql, data_rows, status, category
        )
        latency_metric = self.calculate_latency(latency)

        overall_passed = retrieval.passed and fidelity.passed

        eval_result = EvaluationResult(
            question=question,
            timestamp=datetime.now().isoformat(),
            status=status,
            sql_generated=sql[:500] if sql else "",
            data_rows=data_rows,
            insights=insights[:500] if insights else "",
            retrieval_accuracy=retrieval.score,
            generation_fidelity=fidelity.score,
            latency_seconds=latency,
            retrieval_passed=retrieval.passed,
            fidelity_passed=fidelity.passed,
            overall_passed=overall_passed,
            retrieval_details=retrieval.details,
            fidelity_details=fidelity.details,
            category=category or "",
            expected_table=expected_table or ""
        )

        self.results.append(eval_result)
        return eval_result

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all evaluated queries."""
        if not self.results:
            return {
                "total_queries": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "avg_retrieval_accuracy": 0.0,
                "avg_generation_fidelity": 0.0,
                "avg_latency": 0.0,
                "latency_p50": 0.0,
                "latency_p95": 0.0
            }

        total = len(self.results)
        passed = sum(1 for r in self.results if r.overall_passed)

        latencies = sorted([r.latency_seconds for r in self.results])
        p50_idx = int(len(latencies) * 0.5)
        p95_idx = int(len(latencies) * 0.95)

        return {
            "total_queries": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "avg_retrieval_accuracy": sum(r.retrieval_accuracy for r in self.results) / total,
            "avg_generation_fidelity": sum(r.generation_fidelity for r in self.results) / total,
            "avg_latency": sum(r.latency_seconds for r in self.results) / total,
            "latency_p50": latencies[p50_idx] if latencies else 0,
            "latency_p95": latencies[p95_idx] if latencies else 0,
            "by_category": self._get_category_breakdown()
        }

    def _get_category_breakdown(self) -> Dict[str, Dict]:
        """Get metrics breakdown by category."""
        categories = {}
        for r in self.results:
            cat = r.category or "unknown"
            if cat not in categories:
                categories[cat] = {
                    "total": 0,
                    "passed": 0,
                    "retrieval_sum": 0.0,
                    "fidelity_sum": 0.0,
                    "latency_sum": 0.0
                }
            categories[cat]["total"] += 1
            categories[cat]["passed"] += 1 if r.overall_passed else 0
            categories[cat]["retrieval_sum"] += r.retrieval_accuracy
            categories[cat]["fidelity_sum"] += r.generation_fidelity
            categories[cat]["latency_sum"] += r.latency_seconds

        # Calculate averages
        for cat, data in categories.items():
            if data["total"] > 0:
                data["pass_rate"] = data["passed"] / data["total"]
                data["avg_retrieval"] = data["retrieval_sum"] / data["total"]
                data["avg_fidelity"] = data["fidelity_sum"] / data["total"]
                data["avg_latency"] = data["latency_sum"] / data["total"]

        return categories

    def clear_results(self):
        """Clear all stored results."""
        self.results = []
