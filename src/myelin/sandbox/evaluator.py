from typing import Callable, List, Dict, Any
from dataclasses import dataclass
from ..mining.slicer import DecisionPoint

@dataclass
class EvaluationReport:
    total_decisions: int
    answered_count: int
    unsure_count: int
    correct_matches: int
    agreement_rate: float
    coverage_rate: float
    passed_gate: bool
    tokens_saved_estimate: int

class SandboxEvaluator:
    """Evaluates a compiled habit on held-out test decisions in a strict sandbox."""

    def __init__(self, target_arg: str, min_agreement: float = 0.98, avg_tokens: int = 2500):
        self.target_arg = target_arg
        self.min_agreement = min_agreement
        self.avg_tokens = avg_tokens

    def evaluate(self, func: Callable[[str], Any], test_set: List[DecisionPoint]) -> EvaluationReport:
        total = len(test_set)
        unsure_count = 0
        correct = 0
        answered = 0

        for d in test_set:
            gold_value = d.tool_args.get(self.target_arg)
            try:
                prediction = func(d.user_prompt)
            except Exception:
                prediction = "unsure"

            if prediction == "unsure" or prediction is None:
                unsure_count += 1
            else:
                answered += 1
                if str(prediction).strip() == str(gold_value).strip():
                    correct += 1

        agreement_rate = (correct / answered) if answered > 0 else 0.0
        coverage_rate = (answered / total) if total > 0 else 0.0
        passed = (agreement_rate >= self.min_agreement) and (answered > 0)
        tokens_saved = int(answered * self.avg_tokens)

        return EvaluationReport(
            total_decisions=total,
            answered_count=answered,
            unsure_count=unsure_count,
            correct_matches=correct,
            agreement_rate=round(agreement_rate, 4),
            coverage_rate=round(coverage_rate, 4),
            passed_gate=passed,
            tokens_saved_estimate=tokens_saved
        )
