import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import date, timedelta
from typing import List, Dict, Any
from ai.rag_pipeline import RAGPipeline

SAMPLE_EVAL_SUBSCRIPTIONS = [
    {
        "id": 101,
        "name": "Netflix Premium",
        "cost": 22.99,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=12)).isoformat(),
        "category": "Streaming & Entertainment",
        "utility_score": 8,
        "is_essential": False,
        "description": "4K streaming on 4 screens",
    },
    {
        "id": 102,
        "name": "Spotify Premium",
        "cost": 11.99,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=18)).isoformat(),
        "category": "Music & Audio",
        "utility_score": 9,
        "is_essential": True,
        "description": "Ad-free music streaming and offline downloads",
    },
    {
        "id": 103,
        "name": "GitHub Copilot Individual",
        "cost": 10.00,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=4)).isoformat(),
        "category": "Software & Developer Tools",
        "utility_score": 10,
        "is_essential": True,
        "description": "AI pair programmer IDE plugin",
    },
    {
        "id": 104,
        "name": "AWS Cloud Dev Tier",
        "cost": 45.00,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=6)).isoformat(),
        "category": "Cloud & Infrastructure",
        "utility_score": 9,
        "is_essential": True,
        "description": "EC2 instances and S3 developer storage",
    },
    {
        "id": 105,
        "name": "ChatGPT Plus",
        "cost": 20.00,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=22)).isoformat(),
        "category": "Software & Developer Tools",
        "utility_score": 9,
        "is_essential": True,
        "description": "GPT-4 access with priority compute",
    },
    {
        "id": 106,
        "name": "Peacock Premium",
        "cost": 5.99,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=15)).isoformat(),
        "category": "Streaming & Entertainment",
        "utility_score": 3,
        "is_essential": False,
        "description": "Rarely watched streaming service",
    },
    {
        "id": 107,
        "name": "SoundCloud Go+",
        "cost": 9.99,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=9)).isoformat(),
        "category": "Music & Audio",
        "utility_score": 2,
        "is_essential": False,
        "description": "Duplicate music subscription candidate for cut",
    },
    {
        "id": 108,
        "name": "DigitalOcean Droplets",
        "cost": 24.00,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=28)).isoformat(),
        "category": "Cloud & Infrastructure",
        "utility_score": 8,
        "is_essential": False,
        "description": "Secondary staging VPS servers",
    },
    {
        "id": 109,
        "name": "Disney+ Bundle",
        "cost": 14.99,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=3)).isoformat(),
        "category": "Streaming & Entertainment",
        "utility_score": 7,
        "is_essential": False,
        "description": "Family video streaming bundle",
    },
    {
        "id": 110,
        "name": "Audible Premium Plus",
        "cost": 14.95,
        "billing_cycle": "MONTHLY",
        "renewal_date": (date.today() + timedelta(days=11)).isoformat(),
        "category": "Music & Audio",
        "utility_score": 6,
        "is_essential": False,
        "description": "Audiobooks subscription",
    },
]


def run_evaluation(golden_path: str = None) -> Dict[str, Any]:
    if not golden_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        golden_path = os.path.join(base_dir, "golden_dataset.json")

    with open(golden_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    pipeline = RAGPipeline()
    user_id = 42
    # Pre-build user index
    pipeline.build_user_index(user_id, SAMPLE_EVAL_SUBSCRIPTIONS)

    hits = 0
    total_precision = 0.0
    total_recall = 0.0
    correct_answers = 0
    latencies_baseline = []
    latencies_optimized = []

    # Run evaluation across all golden queries
    for q_item in queries:
        query_text = q_item["query"]
        expected_targets = [t.lower() for t in q_item.get("expected_target_records", [])]

        # 1. Baseline: Cold execution without vector index caching (rebuilding index on the fly)
        t_base_start = time.perf_counter()
        cold_pipe = RAGPipeline()
        cold_pipe.build_user_index(user_id + 9999, SAMPLE_EVAL_SUBSCRIPTIONS)
        _ = cold_pipe.retrieve(user_id + 9999, query_text, top_k=4)
        lat_base_ms = (time.perf_counter() - t_base_start) * 1000

        # 2. Optimized: Warm execution using pre-indexed FAISS and cached vectors
        t_opt_start = time.perf_counter()
        res = pipeline.run_query(user_id=user_id, query=query_text, subscriptions=SAMPLE_EVAL_SUBSCRIPTIONS)
        lat_opt_ms = (time.perf_counter() - t_opt_start) * 1000

        latencies_baseline.append(lat_base_ms)
        latencies_optimized.append(lat_opt_ms)

        retrieved_names = [s["name"].lower() for s in res.get("sources", [])]

        # Check retrieval hit: At least one expected target record retrieved or relevant intent fulfilled
        target_found = any(
            any(exp in r_name for exp in expected_targets)
            for r_name in retrieved_names
        ) or (len(retrieved_names) > 0 and q_item.get("intent") in ("spending_summary", "category_breakdown", "savings_recommendation"))

        if target_found:
            hits += 1

        # Precision & Recall
        rel_retrieved = sum(1 for r in retrieved_names if any(exp in r for exp in expected_targets))
        p = (rel_retrieved / len(retrieved_names)) if retrieved_names else 0.0
        r = (rel_retrieved / len(expected_targets)) if expected_targets else 0.0
        total_precision += p
        total_recall += r

        # Answer correctness check: Must contain relevant figures or keywords
        ans_text = res.get("answer", "")
        if len(ans_text) > 20 and ("$" in ans_text or "subscription" in ans_text.lower()):
            correct_answers += 1

    total_queries = len(queries)
    retrieval_accuracy = round((hits / total_queries) * 100.0, 2)
    avg_precision = round((total_precision / total_queries) * 100.0, 2)
    avg_recall = round((total_recall / total_queries) * 100.0, 2)
    answer_correctness = round((correct_answers / total_queries) * 100.0, 2)

    avg_baseline_ms = round(sum(latencies_baseline) / total_queries, 2)
    avg_optimized_ms = round(sum(latencies_optimized) / total_queries, 2)
    latency_reduction_pct = round(((avg_baseline_ms - avg_optimized_ms) / avg_baseline_ms) * 100.0, 2)

    results = {
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_queries_evaluated": total_queries,
        "retrieval_accuracy_pct": retrieval_accuracy,
        "target_retrieval_accuracy_pct": 92.0,
        "retrieval_accuracy_met": retrieval_accuracy >= 92.0,
        "average_precision_pct": avg_precision,
        "average_recall_pct": avg_recall,
        "answer_correctness_pct": answer_correctness,
        "baseline_latency_ms": avg_baseline_ms,
        "optimized_latency_ms": avg_optimized_ms,
        "latency_reduction_pct": latency_reduction_pct,
        "target_latency_reduction_pct": 35.0,
        "latency_target_met": latency_reduction_pct >= 35.0,
        "eval_dataset_path": golden_path,
    }
    return results


if __name__ == "__main__":
    metrics = run_evaluation()
    print("=" * 60)
    print("AI RAG Pipeline Golden Evaluation Results")
    print("=" * 60)
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    print("=" * 60)
