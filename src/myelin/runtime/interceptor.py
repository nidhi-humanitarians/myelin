from typing import Any, Callable, Dict, Optional
from .registry import HabitRegistry

class MyelinInterceptor:
    """Fast-path dispatcher wrapping agent decision points."""

    def __init__(self, registry: HabitRegistry, fallback_client: Optional[Any] = None):
        self.registry = registry
        self.fallback_client = fallback_client
        self.stats = {"fast_path_hits": 0, "fallbacks": 0}

    def execute_or_fallback(self, habit_name: str, input_text: str, fallback_fn: Callable[[str], Any]) -> Any:
        func = self.registry.habits.get(habit_name)
        if func:
            try:
                res = func(input_text)
                if res != "unsure" and res is not None:
                    self.stats["fast_path_hits"] += 1
                    return res
            except Exception:
                pass

        self.stats["fallbacks"] += 1
        return fallback_fn(input_text)
