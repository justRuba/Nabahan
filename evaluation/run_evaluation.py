# evaluation/run_evaluation.py
# Nabahan Agent - Complete Evaluation Pipeline
# Runs tests, calculates metrics, generates visualizations, and saves CSV report

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.metrics import NabahanMetrics, EvaluationResult
from evaluation.visualize import EvaluationVisualizer
from agent.nabahan_logic import nabahan_agent


class NabahanEvaluationPipeline:
    """
    Complete evaluation pipeline for Nabahan Text-to-SQL agent.

    Features:
    - Runs test cases against the agent
    - Measures Retrieval Accuracy, Generation Fidelity, Latency
    - Generates visualization charts
    - Saves detailed CSV report
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = NabahanMetrics()
        self.visualizer = EvaluationVisualizer(str(self.output_dir / "charts"))

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_test_cases(self, filepath: Optional[str] = None) -> List[Dict]:
        """Load test cases from JSON file."""
        if filepath is None:
            filepath = Path(__file__).parent / "test_cases.json"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Test cases file not found: {filepath}")
            return self._get_default_test_cases()

    def _get_default_test_cases(self) -> List[Dict]:
        """Default test cases if file not found."""
        return [
            {"question": "كم عدد المناقصات الحالية؟", "category": "count", "expected_table": "tenders_full_details"},
            {"question": "كم عدد المشاريع المستقبلية؟", "category": "count", "expected_table": "future_projects"},
            {"question": "المناقصات في منطقة الرياض", "category": "region_filter", "expected_table": "tenders_full_details"},
            {"question": "اكثر الجهات الحكومية مناقصات", "category": "aggregation", "expected_table": "tenders_full_details"},
            {"question": "توزيع المناقصات حسب الحالة", "category": "distribution", "expected_table": "tenders_full_details"},
            {"question": "ما هي المناطق السعودية؟", "category": "lookup", "expected_table": "regions"},
            {"question": "ما هو الطقس اليوم؟", "category": "out_of_scope"},
        ]

    def run_single_test(self, test_case: Dict) -> EvaluationResult:
        """Run evaluation on a single test case."""
        question = test_case.get('question', '')
        filters = test_case.get('filters')
        expected_table = test_case.get('expected_table')
        category = test_case.get('category')

        # Start timing
        self.metrics.start_timer()

        # Call the agent
        try:
            result = nabahan_agent(question, filters)
        except Exception as e:
            result = {
                'status': 'error',
                'data': None,
                'insights': f"Error: {str(e)}",
                'sql': '',
                'chart_type': 'none'
            }

        # Stop timing
        latency = self.metrics.stop_timer()

        # Evaluate
        eval_result = self.metrics.evaluate_query(
            question=question,
            result=result,
            latency=latency,
            expected_table=expected_table,
            category=category
        )

        return eval_result

    def run_full_evaluation(self, test_cases: List[Dict] = None) -> Dict[str, Any]:
        """
        Run complete evaluation pipeline.

        Returns summary with all metrics.
        """
        if test_cases is None:
            test_cases = self.load_test_cases()

        print("=" * 70)
        print("NABAHAN AGENT - EVALUATION PIPELINE")
        print("=" * 70)
        print(f"Timestamp: {self.timestamp}")
        print(f"Test Cases: {len(test_cases)}")
        print(f"Output Dir: {self.output_dir}")
        print("=" * 70)

        results = []

        for i, tc in enumerate(test_cases, 1):
            question = tc.get('question', '')[:50]
            category = tc.get('category', 'unknown')

            print(f"\n[{i}/{len(test_cases)}] {category.upper()}")
            print(f"    Q: {question}...")

            eval_result = self.run_single_test(tc)
            results.append(eval_result)

            status_icon = "PASS" if eval_result.overall_passed else "FAIL"
            print(f"    Retrieval: {eval_result.retrieval_accuracy:.0%} | "
                  f"Fidelity: {eval_result.generation_fidelity:.0%} | "
                  f"Latency: {eval_result.latency_seconds:.2f}s | "
                  f"[{status_icon}]")

        # Get summary
        summary = self.metrics.get_summary()

        # Print summary
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        print(f"Total Queries:           {summary['total_queries']}")
        print(f"Passed:                  {summary['passed']}")
        print(f"Failed:                  {summary['failed']}")
        print(f"Pass Rate:               {summary['pass_rate']*100:.1f}%")
        print("-" * 40)
        print(f"Avg Retrieval Accuracy:  {summary['avg_retrieval_accuracy']*100:.1f}%")
        print(f"Avg Generation Fidelity: {summary['avg_generation_fidelity']*100:.1f}%")
        print("-" * 40)
        print(f"Avg Latency:             {summary['avg_latency']:.2f}s")
        print(f"P50 Latency:             {summary['latency_p50']:.2f}s")
        print(f"P95 Latency:             {summary['latency_p95']:.2f}s")
        print("=" * 70)

        return {
            'summary': summary,
            'results': results,
            'test_cases': test_cases
        }

    def save_csv_report(self, results: List[EvaluationResult], summary: Dict) -> str:
        """
        Save detailed results to CSV file.
        """
        filename = f"evaluation_results_{self.timestamp}.csv"
        filepath = self.output_dir / filename

        # Detailed results CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Query #', 'Timestamp', 'Question', 'Category', 'Expected Table',
                'Status', 'SQL Generated', 'Data Rows', 'Insights',
                'Retrieval Accuracy', 'Generation Fidelity', 'Latency (s)',
                'Retrieval Passed', 'Fidelity Passed', 'Overall Passed',
                'Retrieval Details', 'Fidelity Details'
            ])

            # Data rows
            for i, r in enumerate(results, 1):
                writer.writerow([
                    i,
                    r.timestamp,
                    r.question,
                    r.category,
                    r.expected_table,
                    r.status,
                    r.sql_generated[:200] if r.sql_generated else '',
                    r.data_rows,
                    r.insights[:300] if r.insights else '',
                    f"{r.retrieval_accuracy:.2f}",
                    f"{r.generation_fidelity:.2f}",
                    f"{r.latency_seconds:.3f}",
                    r.retrieval_passed,
                    r.fidelity_passed,
                    r.overall_passed,
                    r.retrieval_details,
                    r.fidelity_details
                ])

        print(f"\nDetailed results saved to: {filepath}")
        return str(filepath)

    def save_summary_csv(self, summary: Dict) -> str:
        """
        Save summary statistics to CSV file.
        """
        filename = f"evaluation_summary_{self.timestamp}.csv"
        filepath = self.output_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Summary metrics
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Queries', summary['total_queries']])
            writer.writerow(['Passed', summary['passed']])
            writer.writerow(['Failed', summary['failed']])
            writer.writerow(['Pass Rate', f"{summary['pass_rate']*100:.1f}%"])
            writer.writerow(['Avg Retrieval Accuracy', f"{summary['avg_retrieval_accuracy']*100:.1f}%"])
            writer.writerow(['Avg Generation Fidelity', f"{summary['avg_generation_fidelity']*100:.1f}%"])
            writer.writerow(['Avg Latency (s)', f"{summary['avg_latency']:.2f}"])
            writer.writerow(['P50 Latency (s)', f"{summary['latency_p50']:.2f}"])
            writer.writerow(['P95 Latency (s)', f"{summary['latency_p95']:.2f}"])

            # Category breakdown
            writer.writerow([])
            writer.writerow(['Category Breakdown'])
            writer.writerow(['Category', 'Total', 'Passed', 'Pass Rate', 'Avg Retrieval', 'Avg Fidelity', 'Avg Latency'])

            if 'by_category' in summary:
                for cat, data in summary['by_category'].items():
                    writer.writerow([
                        cat,
                        data.get('total', 0),
                        data.get('passed', 0),
                        f"{data.get('pass_rate', 0)*100:.1f}%",
                        f"{data.get('avg_retrieval', 0)*100:.1f}%",
                        f"{data.get('avg_fidelity', 0)*100:.1f}%",
                        f"{data.get('avg_latency', 0):.2f}s"
                    ])

        print(f"Summary saved to: {filepath}")
        return str(filepath)

    def generate_visualizations(self, summary: Dict, results: List[EvaluationResult]) -> Dict[str, str]:
        """
        Generate all visualization charts.
        """
        # Convert EvaluationResult objects to dicts for visualization
        results_dicts = [
            {
                'question': r.question,
                'retrieval_accuracy': r.retrieval_accuracy,
                'generation_fidelity': r.generation_fidelity,
                'latency_seconds': r.latency_seconds,
                'overall_passed': r.overall_passed,
                'category': r.category
            }
            for r in results
        ]

        charts = self.visualizer.generate_all_charts(summary, results_dicts)
        return charts

    def run_complete_pipeline(self, test_cases: List[Dict] = None) -> Dict[str, Any]:
        """
        Run the complete evaluation pipeline:
        1. Execute all test cases
        2. Calculate metrics
        3. Generate visualizations
        4. Save CSV reports

        Returns complete results package.
        """
        # Run evaluation
        eval_data = self.run_full_evaluation(test_cases)

        # Save CSV reports
        print("\n" + "-" * 40)
        print("Saving reports...")
        detailed_csv = self.save_csv_report(eval_data['results'], eval_data['summary'])
        summary_csv = self.save_summary_csv(eval_data['summary'])

        # Generate visualizations
        print("\n" + "-" * 40)
        charts = self.generate_visualizations(eval_data['summary'], eval_data['results'])

        print("\n" + "=" * 70)
        print("EVALUATION COMPLETE")
        print("=" * 70)
        print(f"\nOutput files:")
        print(f"  - Detailed CSV: {detailed_csv}")
        print(f"  - Summary CSV:  {summary_csv}")
        print(f"  - Charts:       {self.visualizer.output_dir}")
        for name, path in charts.items():
            print(f"      - {name}: {Path(path).name}")

        return {
            'summary': eval_data['summary'],
            'results': eval_data['results'],
            'csv_files': {
                'detailed': detailed_csv,
                'summary': summary_csv
            },
            'charts': charts
        }


def main():
    """Main entry point for evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description='Nabahan Agent Evaluation Pipeline')
    parser.add_argument('--test-file', type=str, default=None,
                        help='Path to test cases JSON file')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Output directory for results')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick test with fewer cases')
    args = parser.parse_args()

    # Initialize pipeline
    pipeline = NabahanEvaluationPipeline(output_dir=args.output_dir)

    # Load test cases
    if args.test_file:
        test_cases = pipeline.load_test_cases(args.test_file)
    else:
        test_cases = pipeline.load_test_cases()

    # Quick mode - use fewer test cases
    if args.quick:
        test_cases = test_cases[:5]
        print(f"Quick mode: Using {len(test_cases)} test cases")

    # Run pipeline
    results = pipeline.run_complete_pipeline(test_cases)

    # Print final pass rate
    print(f"\n{'='*70}")
    print(f"FINAL PASS RATE: {results['summary']['pass_rate']*100:.1f}%")
    print(f"{'='*70}")

    return results


if __name__ == "__main__":
    main()
