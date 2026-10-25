import argparse
import sys
import os

from myelin.mining.slicer import TrajectorySlicer
from myelin.clustering.clusterer import HabitClusterer
from myelin.sandbox.evaluator import SandboxEvaluator
from myelin.visualizer.dashboard import generate_dashboard
from myelin.runtime.registry import HabitRegistry

def main():
    parser = argparse.ArgumentParser(prog="myelin", description="Myelin: Semantic JIT Compiler for AI Agents")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. Mine
    mine_parser = subparsers.add_parser("mine", help="Extract decision points from trajectory logs")
    mine_parser.add_argument("--input", required=True, help="Path to raw trajectory JSON file")

    # 2. Cluster
    cluster_parser = subparsers.add_parser("cluster", help="Group decisions into habits and check >=50 count")
    cluster_parser.add_argument("--input", required=True, help="Path to raw trajectory JSON file")

    # 3. Evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Score compiled habit on held-out 30% test set")
    eval_parser.add_argument("--data", required=True, help="Trajectory file path")
    eval_parser.add_argument("--habit", required=True, help="Habit name (e.g. extract_user_id)")

    # 4. Dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Export monthly visual dashboard")
    dash_parser.add_argument("--output", default="dashboard.html", help="Output HTML file path")

    args = parser.parse_args()

    if args.command == "mine":
        print(f"Mining decisions from: {args.input}")
        decisions = TrajectorySlicer.slice_tau_bench(args.input)
        print(f"Successfully extracted {len(decisions)} atomic decision points.")

    elif args.command == "cluster":
        print(f"Clustering decisions from: {args.input}")
        decisions = TrajectorySlicer.slice_tau_bench(args.input)
        clusterer = HabitClusterer(min_cluster_size=50)
        clusters = clusterer.cluster_by_tool(decisions)
        print(f"Found {len(clusters)} qualifying habit clusters (>= 50 occurrences):")
        for tool, d_list in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True):
            train, test = clusterer.create_chronological_split(d_list)
            print(f"  - {tool:30s}: {len(d_list):4d} items (Train: {len(train)}, Test: {len(test)})")

    elif args.command == "dashboard":
        generate_dashboard(args.output)

    elif args.command == "evaluate":
        print(f"Evaluating habit '{args.habit}' against {args.data}...")
        decisions = TrajectorySlicer.slice_tau_bench(args.data)
        # Filter for relevant tool
        tool_name = "get_user_details" if "user" in args.habit else "get_reservation_details"
        target_arg = "user_id" if "user" in args.habit else "reservation_id"

        filtered = [d for d in decisions if d.tool_name == tool_name]
        clusterer = HabitClusterer()
        train, test = clusterer.create_chronological_split(filtered)

        # Load habit
        registry = HabitRegistry(os.path.join(os.path.dirname(__file__), "..", "..", "compiled_habits"))
        func = registry.habits.get(args.habit)
        if not func:
            print(f"Error: Habit '{args.habit}' not found in compiled_habits/ registry.")
            return

        evaluator = SandboxEvaluator(target_arg=target_arg)
        report = evaluator.evaluate(func, test)

        print("
=== Evaluation Results ===")
        print(f"Total Test Decisions:     {report.total_decisions}")
        print(f"Handled Decisions:        {report.answered_count} (Coverage: {report.coverage_rate * 100:.1f}%)")
        print(f"Abstained ('unsure'):     {report.unsure_count}")
        print(f"Correct Answers:          {report.correct_matches}")
        print(f"Agreement Rate:           {report.agreement_rate * 100:.2f}% (Required: >= 98.0%)")
        print(f"Gate Status:              {'PASSED' if report.passed_gate else 'REJECTED'}")
        print(f"Tokens Saved Estimate:    {report.tokens_saved_estimate:,} tokens")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
