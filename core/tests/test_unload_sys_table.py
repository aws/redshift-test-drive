from unittest.mock import patch, mock_open, MagicMock
from core.replay.unload_sys_table import UnloadSysTable
from core.replay.prep import ReplayPrep
import unittest


config = {
    "tag": "",
    "workload_location": "test-location/extract",
    "target_cluster_endpoint": "test-redshift-test-testing.us-east-1.redshift.amazonaws.com:5439/dev",
    "target_cluster_region": "us-east-1",
    "master_username": "awsuser",
    "nlb_nat_dns": None,
    "odbc_driver": None,
    "default_interface": "psql",
    "time_interval_between_transactions": "all off",
    "time_interval_between_queries": "all off",
    "execute_copy_statements": "false",
    "execute_unload_statements": "false",
    "replay_output": "s3://location/replay",
    "analysis_output": "s3://location/analysis",
    "unload_system_table_queries": "unload_system_tables.sql",
    "target_cluster_system_table_unload_iam_role": "arn:iam:role/test",
}

replay_id = "2023-02-13T04:59:40.864968+00:00_test-redshift-test-testing_76f32"

file = mock_open(read_data=("--stl_test\nselect * from stl_test"))
file_2 = mock_open(
    read_data=("--stl_unload\nunload (select * from stl_unload) to '' credentials ''")
)
file_3 = mock_open(read_data=("--stl_test\nselect * from stl_test"))

conn = MagicMock()
cursor = MagicMock()

cursor.execute.return_value = True
conn.cursor.return_value = cursor


def mock_get_connection_cred(self, val, max_attempts):
    return {
        "host": "somehost",
        "port": 5437,
        "username": "myname",
        "password": "cantshare",
        "database": "idk",
        "odbc_driver": None,
    }


def mock_db_connect(interface, host, port, username, password, database, odbc_driver):
    return conn


def mock_db_connect_error(interface, host, port, username, password, database, odbc_driver):
    cursor.execute.side_effect = KeyError
    conn.cursor.return_value = cursor

    return conn


class TestReplay(unittest.TestCase):
    @patch.object(ReplayPrep, "get_connection_credentials", mock_get_connection_cred)
    @patch("core.replay.unload_sys_table.db_connect", mock_db_connect)
    @patch("core.replay.unload_sys_table.logger.debug")
    @patch("builtins.open", file)
    @patch("core.replay.prep.boto3")
    def test_unload_system_table(self, mock_boto, mock_debug):
        unload_object = UnloadSysTable(config, replay_id)
        unload_object.unload_system_table()

        mock_debug.assert_called_once_with("Executed unload query: stl_test")

    @patch.object(ReplayPrep, "get_connection_credentials", mock_get_connection_cred)
    @patch("core.replay.unload_sys_table.db_connect", mock_db_connect)
    @patch("core.replay.unload_sys_table.logger.debug")
    @patch("builtins.open", file_2)
    @patch("core.replay.prep.boto3")
    def test_unload_system_table_with_unload_query(self, mock_boto, mock_debug):
        unload_object = UnloadSysTable(config, replay_id)

        unload_object.unload_system_table()

        mock_debug.assert_called_once_with(
            "Executed unload query: stl_unload"
        )

    @patch.object(ReplayPrep, "get_connection_credentials", mock_get_connection_cred)
    @patch("core.replay.unload_sys_table.db_connect", mock_db_connect_error)
    @patch("core.replay.unload_sys_table.logger.error")
    @patch("builtins.open", file_3)
    @patch("core.replay.prep.boto3")
    def test_unload_system_table_with_error(self, mock_boto, mock_error):
        unload_object = UnloadSysTable(config, replay_id)

        unload_object.unload_system_table()

        mock_error.assert_called_once_with("Failed to unload query. ")
