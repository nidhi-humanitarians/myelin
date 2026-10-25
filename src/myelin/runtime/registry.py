import os
import importlib.util
from typing import Dict, Callable, Any

class HabitRegistry:
    """Loads and indexes verified compiled habits from disk."""

    def __init__(self, habits_dir: str):
        self.habits_dir = habits_dir
        self.habits: Dict[str, Callable[[str], Any]] = {}
        self.load_habits()

    def load_habits(self):
        if not os.path.exists(self.habits_dir):
            return

        for item in os.listdir(self.habits_dir):
            habit_path = os.path.join(self.habits_dir, item, "function.py")
            if os.path.isfile(habit_path):
                spec = importlib.util.spec_from_file_location(f"habit_{item}", habit_path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "execute"):
                        self.habits[item] = getattr(mod, "execute")
