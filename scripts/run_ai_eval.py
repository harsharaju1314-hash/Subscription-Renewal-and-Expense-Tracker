#!/usr/bin/env python3
"""
AI RAG Pipeline Golden Evaluation Runner
Evaluates 210 financial queries against ground-truth targets.
Computes retrieval accuracy, precision, recall, answer correctness, and latency reduction.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.eval.evaluator import run_evaluation


def main():
    print("=" * 70)
    print("Executing 200+ Query AI Evaluation Benchmark...")
    print("=" * 70)
    report = run_evaluation()

    out_file = os.path.join(os.path.dirname(__file__), "..", "performance-tests", "ai_evaluation_report.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Total Queries Evaluated:       {report['total_queries_evaluated']}")
    print(f"Retrieval Accuracy:           {report['retrieval_accuracy_pct']}% (Target: >=92.0% -> {'PASSED' if report['retrieval_accuracy_met'] else 'FAILED'})")
    print(f"Average Precision:            {report['average_precision_pct']}%")
    print(f"Average Recall:               {report['average_recall_pct']}%")
    print(f"Answer Correctness:           {report['answer_correctness_pct']}%")
    print(f"Baseline Latency:             {report['baseline_latency_ms']} ms")
    print(f"Optimized Latency:            {report['optimized_latency_ms']} ms")
    print(f"Latency Reduction:            {report['latency_reduction_pct']}% (Target: >=35.0% -> {'PASSED' if report['latency_target_met'] else 'FAILED'})")
    print(f"Benchmark Report Saved:       {out_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
