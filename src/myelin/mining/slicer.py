import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class DecisionPoint:
    decision_id: str
    episode_id: int
    step_idx: int
    tool_name: str
    tool_args: Dict[str, Any]
    user_prompt: str
    system_prompt: Optional[str] = None
    timestamp_idx: int = 0

class TrajectorySlicer:
    """Slices raw multi-turn agent trajectories into atomic decision points."""

    @staticmethod
    def slice_tau_bench(filepath: str) -> List[DecisionPoint]:
        with open(filepath, "r", encoding="utf-8") as f:
            episodes = json.load(f)

        decisions = []
        global_idx = 0

        for ep_idx, ep in enumerate(episodes):
            traj = ep.get("traj", [])
            system_prompt = traj[0].get("content") if traj and traj[0].get("role") == "system" else None

            for step_idx, step in enumerate(traj):
                if step.get("role") == "assistant" and step.get("tool_calls"):
                    # Find preceding user message
                    user_msg = ""
                    for back in range(step_idx - 1, -1, -1):
                        if traj[back].get("role") == "user":
                            user_msg = traj[back].get("content", "")
                            break

                    for tc in step["tool_calls"]:
                        func = tc.get("function", {})
                        tool_name = func.get("name")
                        raw_args = func.get("arguments", "{}")
                        try:
                            tool_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        except json.JSONDecodeError:
                            tool_args = {"raw": raw_args}

                        decisions.append(DecisionPoint(
                            decision_id=f"dec_{ep_idx}_{step_idx}_{global_idx}",
                            episode_id=ep_idx,
                            step_idx=step_idx,
                            tool_name=tool_name,
                            tool_args=tool_args,
                            user_prompt=user_msg,
                            system_prompt=system_prompt,
                            timestamp_idx=global_idx
                        ))
                        global_idx += 1

        return decisions
