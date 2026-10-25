from typing import List, Dict, Any, Optional

class ExactAndFuzzyCache:
    """Baseline A: Simple memorization / normalized string cache of past training pairs."""

    def __init__(self):
        self.cache: Dict[str, Any] = {}

    def fit(self, inputs: List[str], targets: List[Any]):
        for inp, tgt in zip(inputs, targets):
            norm = self._normalize(inp)
            self.cache[norm] = tgt

    def predict(self, text: str) -> Optional[Any]:
        norm = self._normalize(text)
        return self.cache.get(norm, "unsure")

    def _normalize(self, text: str) -> str:
        return " ".join(str(text).lower().split())
