import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from dotenv import load_dotenv
from app.evals.golden_dataset import GOLDEN_DATASET
from app.agent.graph import run_agent
from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def score_answer_relevance(question: str, answer: str) -> float:
    q_emb = model.encode(question)
    a_emb = model.encode(answer)
    return cosine_similarity(q_emb, a_emb)

def score_faithfulness(answer: str, context: str) -> float:
    if not context:
        return 0.5
    a_emb = model.encode(answer)
    c_emb = model.encode(context[:1000])
    return cosine_similarity(a_emb, c_emb)

def score_route_accuracy(expected: str, actual: str) -> float:
    return 1.0 if expected == actual else 0.0

def run_evaluation():
    print("="*60)
    print("HEALTHCLAIM COPILOT — RAGAS-STYLE EVALUATION")
    print("="*60)

    results = []
    total_relevance = 0
    total_faithfulness = 0
    total_route_accuracy = 0

    for i, item in enumerate(GOLDEN_DATASET):
        question = item["question"]
        expected_route = item["expected_route"]

        print(f"\n[{i+1}/{len(GOLDEN_DATASET)}] {question}")

        result = run_agent(question)
        answer = result.get("final_answer", "")
        actual_route = result.get("route", "")
        context = result.get("rag_context") or result.get("sql_result") or ""

        relevance = score_answer_relevance(question, answer)
        faithfulness = score_faithfulness(answer, context)
        route_acc = score_route_accuracy(expected_route, actual_route)

        total_relevance += relevance
        total_faithfulness += faithfulness
        total_route_accuracy += route_acc

        results.append({
            "question": question,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_correct": bool(route_acc),
            "answer_relevance": round(relevance, 3),
            "faithfulness": round(faithfulness, 3),
            "answer_preview": answer[:150]
        })

        print(f"  Route: {expected_route} → {actual_route} {'✅' if route_acc else '❌'}")
        print(f"  Relevance: {relevance:.3f} | Faithfulness: {faithfulness:.3f}")

    n = len(GOLDEN_DATASET)
    avg_relevance = total_relevance / n
    avg_faithfulness = total_faithfulness / n
    avg_route = total_route_accuracy / n

    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Answer Relevance:   {avg_relevance:.3f} / 1.000")
    print(f"Faithfulness:       {avg_faithfulness:.3f} / 1.000")
    print(f"Route Accuracy:     {avg_route:.3f} / 1.000  ({int(avg_route*n)}/{n} correct)")
    print(f"Overall Score:      {(avg_relevance + avg_faithfulness + avg_route)/3:.3f} / 1.000")

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/eval_results.json", "w") as f:
        json.dump({
            "summary": {
                "answer_relevance": round(avg_relevance, 3),
                "faithfulness": round(avg_faithfulness, 3),
                "route_accuracy": round(avg_route, 3),
                "overall": round((avg_relevance + avg_faithfulness + avg_route)/3, 3)
            },
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to data/processed/eval_results.json")
    return results

if __name__ == "__main__":
    run_evaluation()
