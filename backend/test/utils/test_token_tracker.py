import pytest
from utils.token_tracker import TokenTracker


class TestTokenTracker:
    def test_init_empty(self):
        tracker = TokenTracker()
        assert tracker.total_input == 0
        assert tracker.total_output == 0

    def test_add_usage(self):
        tracker = TokenTracker()
        tracker.add("test_node", input_tokens=100, output_tokens=50)
        assert tracker.total_input == 100
        assert tracker.total_output == 50

    def test_add_multiple(self):
        tracker = TokenTracker()
        tracker.add("node1", 100, 50)
        tracker.add("node2", 200, 100)
        assert tracker.total_input == 300
        assert tracker.total_output == 150

    def test_get_summary(self):
        tracker = TokenTracker()
        tracker.add("node1", 100, 50)
        summary = tracker.get_summary()
        assert summary["total_input"] == 100
        assert summary["total_output"] == 50
        assert len(summary["nodes"]) == 1
