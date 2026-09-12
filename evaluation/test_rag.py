import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import retrieve_travel_info
from evaluation.dataset import TEST_DATASET


def evaluate_retrieval():
    print("=" * 70)
    print("TripGenie RAG Evaluation")
    print("=" * 70)

    passed = 0
    total = len(TEST_DATASET)

    for i, test_case in enumerate(TEST_DATASET, start=1):

        query = test_case["query"]
        expected_keywords = test_case["expected_keywords"]

        print(f"\nTest {i}")
        print(f"Question: {query}")
        print("-" * 70)

        result = retrieve_travel_info.invoke({
            "query": query
        })

        result_lower = result.lower()

        matched_keywords = [
            keyword
            for keyword in expected_keywords
            if keyword.lower() in result_lower
        ]

        score = len(matched_keywords) / len(expected_keywords)

        print("Retrieved Context:")
        print(result)

        print("\nEvaluation:")
        print(f"Expected keywords: {expected_keywords}")
        print(f"Matched keywords: {matched_keywords}")
        print(f"Retrieval score: {score:.2f}")

        if score >= 0.5:
            print("Status: PASS")
            passed += 1
        else:
            print("Status: FAIL")

        print("-" * 70)

    overall_score = passed / total

    print("\n" + "=" * 70)
    print("Overall Evaluation")
    print("=" * 70)

    print(f"Passed: {passed}/{total}")
    print(f"Overall Score: {overall_score:.2f}")

    if overall_score >= 0.7:
        print("RAG retrieval quality: GOOD")
    else:
        print("RAG retrieval quality: NEEDS IMPROVEMENT")


if __name__ == "__main__":
    evaluate_retrieval()