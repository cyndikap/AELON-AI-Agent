import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from multi_agent.evaluation.rag_evaluation_runner import evaluate_reference_questions


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AELON RAG evaluation dataset")
    parser.add_argument("--dataset-path", default=None)
    parser.add_argument("--dataset-name", default="rag_reference_questions")
    parser.add_argument("--max-questions", type=int, default=None)
    args = parser.parse_args()

    result = evaluate_reference_questions(
        dataset_path=args.dataset_path,
        dataset_name=args.dataset_name,
        max_questions=args.max_questions,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
