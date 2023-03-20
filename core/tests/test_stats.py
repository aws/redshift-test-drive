import unittest
from unittest.mock import MagicMock, patch, call
from replay.stats import percent, print_stats, display_stats, init_stats, collect_stats
from multiprocessing.managers import SyncManager


stats = {
    "connection_diff_sec": 1.734,
    "query_success": 10,
    "query_error": 2,
    "transaction_success": 10,
    "transaction_error": 2,
    "transaction_error_log": {"test": 3},
    "connection_error_log": {"conn_test": 4},
}

aggregated_stats = {
    "connection_diff_sec": 1,
    "query_success": 10,
    "query_error": 2,
    "transaction_success": 0,
    "transaction_error": 0,
    "transaction_error_log": {},
    "connection_error_log": {},
}


class TestStats(unittest.TestCase):
    def test_percentage(self):
        den = 0
        num = 1

        response = percent(num, den)
        self.assertEqual(response, 0)

    def test_percentage_with_non_zero_den(self):
        den = 100
        num = 10

        response = percent(num, den)
        self.assertEqual(response, 10)

    def test_print_stats(self):
        stats = [1]

        response = print_stats(stats)
        self.assertEqual(response, None)

    @patch("replay.stats.logger.debug")
    def test_print_stats_zero_in_stats(self, mock_logger):
        stats = {
            0: {"connection_diff_sec": 1.734, "query_success": 10, "query_error": 2},
            1: {"connection_diff_sec": 1},
        }

        print_stats(stats)
        calls = [
            call("[0] Max connection offset: +1.734 sec"),
            call("[1] Max connection offset: +1.000 sec"),
            call("Max connection offset: +1.734 sec"),
        ]

        mock_logger.assert_has_calls(calls)

    @patch("replay.stats.logger.info")
    def test_display_stats(self, mock_logger):
        manager = SyncManager()
        manager.start()
        stats = {
            "connection_diff_sec": 1.734,
            "query_success": 10,
            "query_error": 2,
        }

        peak_conn = manager.Value(int, 3)

        display_stats(stats, 100, peak_conn)

        mock_logger.assert_called_once_with(
            "Queries executed: 12 of 100 (12.0%)  [Success: 10 (83.3%), Failed: 2 (16.7%), Peak connections: 3]"
        )

    def test_init_stats(self):
        stats_test_value = {}

        response = init_stats(stats_test_value)
        self.assertEqual(response["connection_diff_sec"], 0)
        self.assertEqual(response["connection_error_log"], {})

    def test_collect_stats_not_stats(self):
        aggregated_stats = {}
        stats = {}

        response = collect_stats(aggregated_stats, stats)
        self.assertEqual(response, None)

    def test_collect_stats(self):
        collect_stats(aggregated_stats, stats)
        self.assertEqual(
            aggregated_stats["connection_diff_sec"], stats["connection_diff_sec"]
        )
        self.assertEqual(
            aggregated_stats["transaction_success"], stats["transaction_success"]
        )
        self.assertEqual(
            aggregated_stats["transaction_error_log"], stats["transaction_error_log"]
        )
