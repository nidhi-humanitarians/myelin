from typing import List, Dict, Tuple
from collections import defaultdict
from ..mining.slicer import DecisionPoint

class HabitClusterer:
    """Discovers recurring decision habits and creates 70/30 chronological splits."""

    def __init__(self, min_cluster_size: int = 50, train_ratio: float = 0.70):
        self.min_cluster_size = min_cluster_size
        self.train_ratio = train_ratio

    def cluster_by_tool(self, decisions: List[DecisionPoint]) -> Dict[str, List[DecisionPoint]]:
        grouped = defaultdict(list)
        for d in decisions:
            grouped[d.tool_name].append(d)

        # Filter for >= min_cluster_size
        qualified = {k: v for k, v in grouped.items() if len(v) >= self.min_cluster_size}
        return qualified

    def create_chronological_split(self, decisions: List[DecisionPoint]) -> Tuple[List[DecisionPoint], List[DecisionPoint]]:
        # Sort by chronological index
        sorted_dec = sorted(decisions, key=lambda x: x.timestamp_idx)
        split_idx = int(len(sorted_dec) * self.train_ratio)
        train_set = sorted_dec[:split_idx]
        test_set = sorted_dec[split_idx:]
        return train_set, test_set
