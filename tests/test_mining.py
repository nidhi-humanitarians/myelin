import os
import pytest
from myelin.mining.slicer import TrajectorySlicer
from myelin.clustering.clusterer import HabitClusterer

def test_slicer_and_clusterer():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "historical_trajectories", "gpt-4o-airline.json")
    if not os.path.exists(data_path):
        pytest.skip("Trajectory file not found")

    decisions = TrajectorySlicer.slice_tau_bench(data_path)
    assert len(decisions) > 500

    clusterer = HabitClusterer(min_cluster_size=50)
    clusters = clusterer.cluster_by_tool(decisions)
    assert "get_reservation_details" in clusters
    assert "get_user_details" in clusters

    res_dec = clusters["get_reservation_details"]
    train, test = clusterer.create_chronological_split(res_dec)
    assert len(train) > len(test)
    assert len(train) + len(test) == len(res_dec)
