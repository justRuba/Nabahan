# evaluation/visualize.py
# Nabahan Agent - Evaluation Visualization
# Generates charts and tables from evaluation results

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files

# Set up for Arabic text support
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Color scheme matching Nabahan branding
COLORS = {
    'primary': '#2fb38e',
    'secondary': '#1a635a',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'light': '#c7f9cc',
    'gray': '#6b7280'
}

GREEN_PALETTE = ['#1a635a', '#2fb38e', '#57cc99', '#80ed99', '#c7f9cc']


class EvaluationVisualizer:
    """
    Visualization generator for Nabahan evaluation results.

    Creates:
    - Bar charts for metrics comparison
    - Pie charts for pass/fail distribution
    - Line charts for latency trends
    - Summary tables
    """

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_metrics_bar_chart(
        self,
        summary: Dict[str, Any],
        filename: str = "metrics_overview.png"
    ) -> str:
        """
        Create bar chart showing average scores for each metric.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['Retrieval\nAccuracy', 'Generation\nFidelity', 'Pass Rate']
        values = [
            summary.get('avg_retrieval_accuracy', 0) * 100,
            summary.get('avg_generation_fidelity', 0) * 100,
            summary.get('pass_rate', 0) * 100
        ]

        bars = ax.bar(metrics, values, color=[COLORS['primary'], COLORS['secondary'], COLORS['success']])

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=12, fontweight='bold')

        ax.set_ylim(0, 110)
        ax.set_ylabel('Score (%)', fontsize=12)
        ax.set_title('Nabahan Agent - Evaluation Metrics Overview', fontsize=14, fontweight='bold')
        ax.axhline(y=60, color=COLORS['warning'], linestyle='--', alpha=0.7, label='Pass Threshold (60%)')
        ax.legend(loc='upper right')

        # Add grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_pass_fail_pie_chart(
        self,
        summary: Dict[str, Any],
        filename: str = "pass_fail_distribution.png"
    ) -> str:
        """
        Create pie chart showing pass/fail distribution.
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)

        if passed + failed == 0:
            passed, failed = 1, 0  # Avoid division by zero

        sizes = [passed, failed]
        labels = [f'Passed\n({passed})', f'Failed\n({failed})']
        colors = [COLORS['success'], COLORS['error']]
        explode = (0.05, 0)

        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            textprops={'fontsize': 12}
        )

        for autotext in autotexts:
            autotext.set_fontweight('bold')
            autotext.set_color('white')

        ax.set_title('Test Results Distribution', fontsize=14, fontweight='bold')

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_latency_chart(
        self,
        results: List[Dict],
        filename: str = "latency_analysis.png"
    ) -> str:
        """
        Create chart showing latency distribution and trends.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        latencies = [r.get('latency_seconds', r.get('latency', 0)) for r in results]

        if not latencies:
            latencies = [0]

        # Left: Histogram
        ax1.hist(latencies, bins=10, color=COLORS['primary'], edgecolor='white', alpha=0.8)
        ax1.axvline(x=sum(latencies)/len(latencies), color=COLORS['error'],
                    linestyle='--', linewidth=2, label=f'Avg: {sum(latencies)/len(latencies):.2f}s')
        ax1.set_xlabel('Latency (seconds)', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Latency Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.yaxis.grid(True, linestyle='--', alpha=0.3)

        # Right: Line chart (query sequence)
        ax2.plot(range(1, len(latencies) + 1), latencies, marker='o',
                 color=COLORS['primary'], linewidth=2, markersize=6)
        ax2.axhline(y=5, color=COLORS['warning'], linestyle='--', alpha=0.7, label='Target: 5s')
        ax2.fill_between(range(1, len(latencies) + 1), latencies,
                         alpha=0.2, color=COLORS['primary'])
        ax2.set_xlabel('Query Number', fontsize=11)
        ax2.set_ylabel('Latency (seconds)', fontsize=11)
        ax2.set_title('Latency per Query', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.yaxis.grid(True, linestyle='--', alpha=0.3)

        plt.suptitle('Nabahan Agent - Latency Analysis', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_category_breakdown_chart(
        self,
        category_data: Dict[str, Dict],
        filename: str = "category_breakdown.png"
    ) -> str:
        """
        Create grouped bar chart showing metrics by query category.
        """
        if not category_data:
            # Create empty chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No category data available', ha='center', va='center')
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return str(filepath)

        fig, ax = plt.subplots(figsize=(12, 6))

        categories = list(category_data.keys())
        x = range(len(categories))
        width = 0.25

        retrieval_scores = [category_data[c].get('avg_retrieval', 0) * 100 for c in categories]
        fidelity_scores = [category_data[c].get('avg_fidelity', 0) * 100 for c in categories]
        pass_rates = [category_data[c].get('pass_rate', 0) * 100 for c in categories]

        bars1 = ax.bar([i - width for i in x], retrieval_scores, width,
                       label='Retrieval Accuracy', color=COLORS['primary'])
        bars2 = ax.bar(x, fidelity_scores, width,
                       label='Generation Fidelity', color=COLORS['secondary'])
        bars3 = ax.bar([i + width for i in x], pass_rates, width,
                       label='Pass Rate', color=COLORS['success'])

        ax.set_xlabel('Category', fontsize=11)
        ax.set_ylabel('Score (%)', fontsize=11)
        ax.set_title('Metrics by Query Category', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.set_ylim(0, 110)
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.axhline(y=60, color=COLORS['warning'], linestyle='--', alpha=0.5)

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_detailed_results_table(
        self,
        results: List[Dict],
        filename: str = "detailed_results.png"
    ) -> str:
        """
        Create a visual table showing detailed results for each query.
        """
        fig, ax = plt.subplots(figsize=(14, max(4, len(results) * 0.5 + 2)))
        ax.axis('off')

        # Prepare table data
        headers = ['#', 'Question (truncated)', 'Retrieval', 'Fidelity', 'Latency', 'Status']
        table_data = []

        for i, r in enumerate(results[:20], 1):  # Limit to 20 rows
            question = r.get('question', '')[:30] + '...' if len(r.get('question', '')) > 30 else r.get('question', '')
            retrieval = r.get('retrieval_accuracy', r.get('retrieval', 0))
            fidelity = r.get('generation_fidelity', r.get('fidelity', 0))
            latency = r.get('latency_seconds', r.get('latency', 0))
            passed = r.get('overall_passed', r.get('passed', False))

            table_data.append([
                str(i),
                question,
                f"{retrieval:.0%}",
                f"{fidelity:.0%}",
                f"{latency:.2f}s",
                'PASS' if passed else 'FAIL'
            ])

        if not table_data:
            table_data = [['', 'No results available', '', '', '', '']]

        table = ax.table(
            cellText=table_data,
            colLabels=headers,
            cellLoc='center',
            loc='center',
            colColours=[COLORS['primary']] * len(headers)
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)

        # Style header
        for i in range(len(headers)):
            table[(0, i)].set_text_props(color='white', fontweight='bold')

        # Color status cells
        for i, row in enumerate(table_data, 1):
            if row[5] == 'PASS':
                table[(i, 5)].set_facecolor(COLORS['light'])
            elif row[5] == 'FAIL':
                table[(i, 5)].set_facecolor('#fecaca')

        ax.set_title('Detailed Evaluation Results', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_summary_dashboard(
        self,
        summary: Dict[str, Any],
        results: List[Dict],
        filename: str = "evaluation_dashboard.png"
    ) -> str:
        """
        Create a comprehensive dashboard with all key visualizations.
        """
        fig = plt.figure(figsize=(16, 12))

        # Title
        fig.suptitle('Nabahan Agent - Evaluation Dashboard', fontsize=18, fontweight='bold', y=0.98)

        # 1. Metrics Overview (top left)
        ax1 = fig.add_subplot(2, 2, 1)
        metrics = ['Retrieval\nAccuracy', 'Generation\nFidelity', 'Pass\nRate']
        values = [
            summary.get('avg_retrieval_accuracy', 0) * 100,
            summary.get('avg_generation_fidelity', 0) * 100,
            summary.get('pass_rate', 0) * 100
        ]
        bars = ax1.bar(metrics, values, color=[COLORS['primary'], COLORS['secondary'], COLORS['success']])
        for bar, val in zip(bars, values):
            ax1.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                         xytext=(0, 3), textcoords="offset points", ha='center', fontweight='bold')
        ax1.set_ylim(0, 110)
        ax1.set_title('Metrics Overview', fontweight='bold')
        ax1.axhline(y=60, color=COLORS['warning'], linestyle='--', alpha=0.7)
        ax1.yaxis.grid(True, linestyle='--', alpha=0.3)

        # 2. Pass/Fail Pie (top right)
        ax2 = fig.add_subplot(2, 2, 2)
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        if passed + failed > 0:
            ax2.pie([passed, failed], labels=[f'Passed ({passed})', f'Failed ({failed})'],
                    colors=[COLORS['success'], COLORS['error']], autopct='%1.1f%%',
                    explode=(0.05, 0), shadow=True, textprops={'fontweight': 'bold'})
        ax2.set_title('Test Results', fontweight='bold')

        # 3. Latency Distribution (bottom left)
        ax3 = fig.add_subplot(2, 2, 3)
        latencies = [r.get('latency_seconds', r.get('latency', 0)) for r in results]
        if latencies:
            ax3.hist(latencies, bins=8, color=COLORS['primary'], edgecolor='white', alpha=0.8)
            avg_lat = sum(latencies) / len(latencies)
            ax3.axvline(x=avg_lat, color=COLORS['error'], linestyle='--',
                        linewidth=2, label=f'Avg: {avg_lat:.2f}s')
            ax3.legend()
        ax3.set_xlabel('Latency (seconds)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Latency Distribution', fontweight='bold')
        ax3.yaxis.grid(True, linestyle='--', alpha=0.3)

        # 4. Summary Stats (bottom right)
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.axis('off')

        stats_text = f"""
        EVALUATION SUMMARY
        {'='*40}

        Total Queries:          {summary.get('total_queries', 0)}
        Passed:                 {summary.get('passed', 0)}
        Failed:                 {summary.get('failed', 0)}
        Pass Rate:              {summary.get('pass_rate', 0)*100:.1f}%

        Avg Retrieval Accuracy: {summary.get('avg_retrieval_accuracy', 0)*100:.1f}%
        Avg Generation Fidelity:{summary.get('avg_generation_fidelity', 0)*100:.1f}%

        Avg Latency:            {summary.get('avg_latency', 0):.2f}s
        P50 Latency:            {summary.get('latency_p50', 0):.2f}s
        P95 Latency:            {summary.get('latency_p95', 0):.2f}s
        """

        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=11,
                 verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='#f3f4f6', alpha=0.8))

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def generate_all_charts(
        self,
        summary: Dict[str, Any],
        results: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate all visualization charts.

        Returns dict mapping chart name to file path.
        """
        charts = {}

        print("Generating visualization charts...")

        # Metrics overview
        charts['metrics_overview'] = self.create_metrics_bar_chart(summary)
        print(f"  Created: {charts['metrics_overview']}")

        # Pass/fail pie
        charts['pass_fail'] = self.create_pass_fail_pie_chart(summary)
        print(f"  Created: {charts['pass_fail']}")

        # Latency analysis
        charts['latency'] = self.create_latency_chart(results)
        print(f"  Created: {charts['latency']}")

        # Category breakdown
        if 'by_category' in summary:
            charts['category_breakdown'] = self.create_category_breakdown_chart(summary['by_category'])
            print(f"  Created: {charts['category_breakdown']}")

        # Detailed results table
        charts['detailed_results'] = self.create_detailed_results_table(results)
        print(f"  Created: {charts['detailed_results']}")

        # Full dashboard
        charts['dashboard'] = self.create_summary_dashboard(summary, results)
        print(f"  Created: {charts['dashboard']}")

        return charts


def main():
    """Test visualization with sample data."""
    # Sample summary data
    summary = {
        'total_queries': 20,
        'passed': 17,
        'failed': 3,
        'pass_rate': 0.85,
        'avg_retrieval_accuracy': 0.90,
        'avg_generation_fidelity': 0.85,
        'avg_latency': 2.5,
        'latency_p50': 2.0,
        'latency_p95': 5.0,
        'by_category': {
            'count': {'avg_retrieval': 0.95, 'avg_fidelity': 0.90, 'pass_rate': 0.95},
            'aggregation': {'avg_retrieval': 0.85, 'avg_fidelity': 0.80, 'pass_rate': 0.80},
            'out_of_scope': {'avg_retrieval': 1.0, 'avg_fidelity': 1.0, 'pass_rate': 1.0},
            'region_filter': {'avg_retrieval': 0.80, 'avg_fidelity': 0.75, 'pass_rate': 0.75}
        }
    }

    # Sample results
    results = [
        {'question': 'كم عدد المناقصات؟', 'retrieval_accuracy': 1.0, 'generation_fidelity': 1.0, 'latency_seconds': 1.5, 'overall_passed': True},
        {'question': 'المشاريع في الرياض', 'retrieval_accuracy': 1.0, 'generation_fidelity': 0.8, 'latency_seconds': 2.3, 'overall_passed': True},
        {'question': 'توزيع المناقصات حسب الحالة', 'retrieval_accuracy': 0.8, 'generation_fidelity': 0.9, 'latency_seconds': 3.1, 'overall_passed': True},
        {'question': 'ما هو الطقس؟', 'retrieval_accuracy': 1.0, 'generation_fidelity': 1.0, 'latency_seconds': 0.5, 'overall_passed': True},
        {'question': 'اكثر الجهات مناقصات', 'retrieval_accuracy': 0.5, 'generation_fidelity': 0.5, 'latency_seconds': 4.2, 'overall_passed': False},
    ]

    visualizer = EvaluationVisualizer()
    charts = visualizer.generate_all_charts(summary, results)

    print(f"\nAll charts saved to: {visualizer.output_dir}")
    for name, path in charts.items():
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()
