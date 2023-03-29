from unittest.mock import patch, mock_open
import unittest
from core.replay.connections_parser import parse_connections

time_interval_between_transactions = "all on"
time_interval_between_queries = "all on"
filters = {
    "include": {"database_name": ["*"], "username": ["*"], "pid": ["*"]},
    "exclude": {"database_name": [], "username": [], "pid": []},
}

open_mock_1 = mock_open(
    read_data=(
        """[{
  "session_initiation_time": "2023-01-09 15:48:15.313000+00:00",
  "disconnection_time": "2023-01-09 15:48:15.872000+00:00",
  "application_name": "",
  "database_name": "dev",
  "username": "awsuser",
  "pid": "1073815778",
  "time_interval_between_transactions": "True",
  "time_interval_between_queries": "transaction"
}]"""
    )
)

open_mock_2 = mock_open(
    read_data=(
        """[{
                "session_initiation_time": "",
                "disconnection_time": "2023-01-09 15:48:15.872000+00:00",
                "application_name": "",
                "database_name": "dev",
                "username": "awsuser",
                "pid": "1073815778",
                "time_interval_between_transactions": "True",
                "time_interval_between_queries": "transaction"
            }]"""
    )
)

open_mock_3 = mock_open(
    read_data=(
        """
        [
            {
                "session_initiation_time": "2023-01-09 15:48:15.313000+00:00",
                "disconnection_time": "",
                "application_name": "",
                "database_name": "dev",
                "username": "awsuser",
                "pid": "1073815778",
                "time_interval_between_transactions": "True",
                "time_interval_between_queries": "transaction"
            }
        ]
    """
    )
)

open_mock_4 = mock_open(
    read_data=(
        """
        [
    {
       "session_initiation_time_error": "2023-01-09 15:48:15.313000+00:00",
       "disconnection_time_error": "2023-01-09 15:48:15.872000+00:00",
       "application_name": "",
       "database_name": "dev",
       "username": "awsuser",
       "pid": "1073815778",
       "time_interval_between_transactions": true,
       "time_interval_between_queries": "transaction"
    }
 ]
    """
    )
)


class TestConnectionsParser(unittest.TestCase):
    @patch("core.replay.connections_parser.client")
    @patch("core.replay.connections_parser.json")
    def test_parse_connections(self, mock_json, mock_client):
        workload_directory = (
            "s3://test/extracts/Edited_Extraction_2023-01-23T09:46:24.784062+00:00"
        )
        mock_json.loads.return_value = [
            {
                "session_initiation_time": "2023-01-09 15:48:15.313000+00:00",
                "disconnection_time": "2023-01-09 15:48:15.872000+00:00",
                "application_name": "",
                "database_name": "dev",
                "username": "awsuser",
                "pid": "1073815778",
                "time_interval_between_transactions": True,
                "time_interval_between_queries": "transaction",
            }
        ]
        mock_client.get_object.return_value = mock_json

        connections, total_connections = parse_connections(
            workload_directory,
            time_interval_between_transactions,
            time_interval_between_queries,
            filters,
        )
        self.assertEqual(connections[0].pid, "1073815778")
        self.assertEqual(total_connections, 1)

    @patch("core.replay.connections_parser.open", open_mock_1)
    def test_parse_connections_s3_location(self):
        workload_directory = "testdata/testlocation"

        connections, total_connections = parse_connections(
            workload_directory,
            time_interval_between_transactions,
            time_interval_between_queries,
            filters,
        )
        self.assertEqual(connections[0].pid, "1073815778")
        self.assertEqual(total_connections, 1)

    @patch("core.replay.connections_parser.open", open_mock_2)
    def test_parse_connections_initiation_time(self):
        workload_directory = "testdata/testlocation"

        connections, total_connections = parse_connections(
            workload_directory,
            time_interval_between_transactions,
            time_interval_between_queries,
            filters,
        )
        self.assertEqual(connections[0].session_initiation_time, None)
        self.assertEqual(total_connections, 1)

    @patch("core.replay.connections_parser.open", open_mock_3)
    def test_parse_connections_disconnection_time(self):
        workload_directory = "testdata/testlocation"

        connections, total_connections = parse_connections(
            workload_directory,
            time_interval_between_transactions,
            time_interval_between_queries,
            filters,
        )
        self.assertEqual(connections[0].disconnection_time, None)
        self.assertEqual(total_connections, 1)

    @patch("core.replay.connections_parser.open", open_mock_4)
    def test_parse_connections_except_case(self):
        workload_directory = "testdata/testlocation"

        connections, total_connections = parse_connections(
            workload_directory,
            time_interval_between_transactions,
            time_interval_between_queries,
            filters,
        )
        self.assertEqual(total_connections, 0)
