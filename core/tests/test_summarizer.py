import unittest
from unittest.mock import patch, mock_open, call
from core.replay.summarizer import summarize, export_errors
import datetime

aggregated_stats = {
    "connection_diff_sec": 1.734,
    "query_success": 10,
    "query_error": 2,
    "transaction_success": 10,
    "transaction_error": 2,
    "transaction_error_log": {"test": [[1, 2], [3, 4]]},
    "connection_error_log": {"conn_test": 4},
}

config = {
    "tag": "",
    "workload_location": "test-location",
    "target_cluster_endpoint": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
    "target_cluster_region": "us-east-1",
    "master_username": "awsuser",
    "nlb_nat_dns": "",
    "odbc_driver": "",
    "default_interface": "psql",
    "time_interval_between_transactions": "all on",
    "time_interval_between_queries": "all on",
    "execute_copy_statements": "false",
    "execute_unload_statements": "false",
    "replay_output": "",
    "analysis_output": "",
    "unload_iam_role": "",
    "analysis_iam_role": "",
    "unload_system_table_queries": "unload_system_tables.sql",
    "target_cluster_system_table_unload_iam_role": "",
    "filters": {
        "include": {"database_name": ["*"], "username": ["*"], "pid": ["*"]},
        "exclude": {"database_name": [], "username": [], "pid": []},
    },
}

transaction_count = 48
query_count = 48
replay_id = "2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab"
replay_start_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
replay_end_time = replay_start_timestamp + datetime.timedelta(hours=1)
connection_logs = [20, 23, 43, 52]

error_file = mock_open()


def mock_export_errors(connection_error_log, transaction_error_log, error_location, replay_id):
    return True


class TestSummarizer(unittest.TestCase):
    @patch("core.replay.summarizer.export_errors")
    def test_summarize(self, mock_export_errors):
        mock_export_errors.return_value = True
        response = summarize(
            connection_logs,
            config,
            replay_start_timestamp,
            aggregated_stats,
            query_count,
            replay_id,
            transaction_count,
            replay_end_time,
        )

        self.assertEqual(len(response), 5)

    @patch("core.replay.summarizer.export_errors", mock_export_errors)
    def test_summarize_zeroDivisionError(self):
        transaction_count = 0
        response = summarize(
            connection_logs,
            config,
            replay_start_timestamp,
            aggregated_stats,
            query_count,
            replay_id,
            transaction_count,
            replay_end_time,
        )

        self.assertEqual(response[1], "Encountered 1 connection errors and 1 transaction errors")

    def test_export_errors_connection_transaction_errors_equals_zero(self):
        response = export_errors({}, {}, config["workload_location"], replay_id)

        self.assertEqual(response, None)

    @patch("builtins.open", error_file)
    @patch("os.makedirs")
    def test_export_errors_local_location(self, mock_os):
        mock_os.side_effect = [
            "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/connection_errors",
            "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/transaction_errors",
        ]

        export_errors(
            aggregated_stats["connection_error_log"],
            aggregated_stats["transaction_error_log"],
            config["workload_location"],
            replay_id,
        )
        calls = [
            call(
                "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/connection_errors"
            ),
            call(
                "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/transaction_errors"
            ),
        ]

        mock_os.assert_has_calls(calls, any_order=False)

        calls = [
            call(
                "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/connection_errors/conn_test.txt",
                "w",
            ),
            call().write(4),
            call().close(),
            call(
                "test-location/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/transaction_errors/test.txt",
                "w",
            ),
            call().write("1\n2\n\n3\n4\n\n"),
            call().close(),
        ]

        error_file.assert_has_calls(calls)

    @patch("botocore.client.BaseClient._make_api_call")
    @patch("core.replay.summarizer.aws_service_helper.s3_put_object")
    @patch("core.replay.summarizer.os")
    def test_export_errors_workloc_s3(self, mock_os, mock_s3, mock_client):
        config["workload_location"] = "s3://test-location"

        mock_os.makedirs.return_value = "workload_location"
        mock_s3.return_value = "put"
        mock_client.return_value = True
        mock_s3.put_object.return_value = "put"

        export_errors(
            aggregated_stats["connection_error_log"],
            aggregated_stats["transaction_error_log"],
            config["workload_location"],
            replay_id,
        )

        mock_s3.assert_called_once_with(
            "test-location",
            4,
            "2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/connection_errors/conn_test.txt",
        )
        mock_client.assert_called_once_with(
            "PutObject",
            {
                "Body": "1\n2\n\n3\n4\n\n",
                "Bucket": "test-location",
                "Key": "2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/transaction_errors/test.txt",
            },
        )

    @patch("botocore.client.BaseClient._make_api_call")
    @patch("core.replay.summarizer.aws_service_helper.s3_put_object")
    @patch("core.replay.summarizer.os")
    def test_export_errors_workloc_s3_with_prefix(self, mock_os, mock_s3, mock_client):
        config["workload_location"] = "s3://test-location/test"

        mock_os.makedirs.return_value = "workload_location"
        mock_s3.return_value = "put"
        mock_client.return_value = True
        mock_s3.put_object.return_value = "put"

        export_errors(
            aggregated_stats["connection_error_log"],
            aggregated_stats["transaction_error_log"],
            config["workload_location"],
            replay_id,
        )

        mock_s3.assert_called_once_with(
            "test-location",
            4,
            "test/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/connection_errors/conn_test.txt",
        )
        mock_client.assert_called_once_with(
            "PutObject",
            {
                "Body": "1\n2\n\n3\n4\n\n",
                "Bucket": "test-location",
                "Key": "test/2023-02-07T19:17:11.472063+00:00_cluster-testing_1ddab/transaction_errors/test.txt",
            },
        )
