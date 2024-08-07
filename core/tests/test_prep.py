import datetime
import unittest
from unittest.mock import patch

import yaml
from dateutil.tz import tzutc

from core.replay.connections_parser import ConnectionLog
from core.replay.prep import ReplayPrep, InvalidFilterException
from core.replay.transactions_parser import TransactionsParser, Transaction, Query


class TestParseFilename(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_filename(self):
        # test parsing a SQL filename
        filename = "mydb1-myuser-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "myuser")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_dash(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "my-user")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_email(self):
        # test parsing a SQL filename
        filename = "mydb1-user@sample.com-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "user@sample.com")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_dash_fail(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-12.345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertTrue(all([_ is None for _ in (db_name, username, pid, xid)]))

    def test_parse_filename_incomplete(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-.txt"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertTrue(all([_ is None for _ in (db_name, username, pid, xid)]))


class TestValidateAndNormalizeFilters(unittest.TestCase):
    def test_exceptions(self):
        # wildcard must be specified by itself
        filter_str = """filters:
                          include:
                              username: ['*', 'joe']
                          exclude:
                              database_name: ['']
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        filter_str = """filters:
                          include:
                              username: ['dave']
                          exclude:
                              database_name: ['*', 'betty']
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        # unsupported filter
        filter_str = """filters:
                          include:
                              doesnt_exist: ['*']
                          exclude:
                              database_name: []
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        filter_str = """filters:
                          include:
                              database_name: ['*']
                          exclude:
                              doesnt_exist: []
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        # include and exclude same field value
        filter_str = """filters:
                          include:
                              database_name: ['user1', 'user2', 'user3']
                          exclude:
                              database_name: ['user4', 'user2']
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        filter_str = """filters:
                          include:
                              database_name: ['*']
                          exclude:
                              database_name: ['*']
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

        # empty filter--include is required
        filter_str = """filters:
                          include:
                              database_name: []
                          exclude:
                              database_name: []
                     """
        with self.assertRaises(InvalidFilterException):
            filters = ReplayPrep.validate_and_normalize_filters(
                ConnectionLog, yaml.safe_load(filter_str)["filters"]
            )

    def test_filter_normalization(self):
        filters = """filters:
                       include:
                           username: ['user1', 'user2']
                       exclude:
                           database_name: ['db1']
                  """
        normalized_filters = """filters:
                       include:
                           pid: ['*']
                           username: ['user1', 'user2']
                           database_name: ['*']
                       exclude:
                           pid: []
                           username: []
                           database_name: ['db1']
                  """
        config1 = yaml.safe_load(filters)
        config2 = yaml.safe_load(normalized_filters)
        self.assertDictEqual(
            config2["filters"],
            ReplayPrep.validate_and_normalize_filters(ConnectionLog, config1["filters"]),
        )

    def test_empty_filter_validation(self):
        normalized_filters = """filters:
                       include:
                           pid: ['*']
                           username: ['*']
                           database_name: ['*']
                       exclude:
                           pid: []
                           username: []
                           database_name: []
                  """
        config1 = {}
        config2 = yaml.safe_load(normalized_filters)
        self.assertDictEqual(
            config2["filters"],
            ReplayPrep.validate_and_normalize_filters(ConnectionLog, config1),
        )


class TestGetConnectionCredentials(unittest.TestCase):
    def test_get_connection_credentials_from_cache(self):
        prep = ReplayPrep({})
        credentials = {"password": "test"}
        prep.credentials_cache["testUsername"] = {
            "last_update": datetime.datetime.now(tz=datetime.timezone.utc),
            "target_cluster_urls": credentials,
        }
        result = prep.get_connection_credentials("testUsername")
        self.assertEqual(result, credentials)

    @patch("core.replay.prep.get_secret")
    def test_get_connection_credentials_serverless_from_secrets_manager(self, mock_get_secret):
        mock_get_secret.return_value = {
            "admin_username": "testAdmin",
            "admin_password": "testPassword",
        }
        prep = ReplayPrep(
            {
                "target_cluster_endpoint": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
                "secret_name": "test_secret",
                "odbc_driver": "test",
                "nlb_nat_dns": None,
                "target_cluster_region": "us-east-1",
            }
        )
        result = prep.get_connection_credentials("testUsername")
        self.assertEqual(
            result["psql"],
            {
                "username": "testAdmin",
                "password": "testPassword",
                "host": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com",
                "port": "5439",
                "database": "dev",
            },
        )

    @patch("core.replay.prep.redshift_get_cluster_credentials")
    def test_get_connection_credentials_serverless_from_redshift_api(self, mock_get_cluster_creds):
        mock_get_cluster_creds.return_value = {"DbUser": "testAdmin", "DbPassword": "testPassword"}
        prep = ReplayPrep(
            {
                "target_cluster_endpoint": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
                "secret_name": None,
                "odbc_driver": "test",
                "nlb_nat_dns": None,
                "target_cluster_region": "us-east-1",
            }
        )
        result = prep.get_connection_credentials("testUsername")
        self.assertEqual(
            result["psql"],
            {
                "username": "testAdmin",
                "password": "testPassword",
                "host": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com",
                "port": "5439",
                "database": "dev",
            },
        )

    @patch("core.replay.prep.redshift_get_cluster_credentials")
    def test_get_connection_credentials_provisioned_from_redshift_api(
        self, mock_get_cluster_creds
    ):
        mock_get_cluster_creds.return_value = {"DbUser": "testAdmin", "DbPassword": "testPassword"}
        prep = ReplayPrep(
            {
                "target_cluster_endpoint": "test.111222333222.us-east-1.redshift.amazonaws.com:5439/dev",
                "odbc_driver": "test",
                "nlb_nat_dns": None,
                "target_cluster_region": "us-east-1",
            }
        )
        result = prep.get_connection_credentials("testUsername")
        self.assertEqual(
            result["psql"],
            {
                "username": "testAdmin",
                "password": "testPassword",
                "host": "test.111222333222.us-east-1.redshift.amazonaws.com",
                "port": "5439",
                "database": "dev",
            },
        )
    
    @patch("core.replay.prep.redshift_get_cluster_credentials")
    def test_get_connection_credentials_for_database_not_being_none(self, mock_get_cluster_creds):
        mock_get_cluster_creds.return_value = {"DbUser": "testAdmin", "DbPassword": "testPassword"}
        prep = ReplayPrep(
            {
                "target_cluster_endpoint": "test.111222333222.us-east-1.redshift.amazonaws.com:5439/dev",
                "odbc_driver": "test",
                "nlb_nat_dns": None,
                "target_cluster_region": "us-east-1",
            }
        )

        result = prep.get_connection_credentials("testUsername","tcpds_100g")
        self.assertEqual(
            result["psql"],
            {
                "username": "testAdmin",
                "password": "testPassword",
                "host": "test.111222333222.us-east-1.redshift.amazonaws.com",
                "port": "5439",
                "database": "tcpds_100g",
            },
        )


class TestCorrelateTransactionsWithConnections(unittest.TestCase):
    @patch.object(TransactionsParser, "__init__", return_value=None)
    @patch.object(TransactionsParser, "parse_transactions")
    @patch("core.replay.prep.parse_connections")
    def test_success(self, patched_parse_connections, patched_parse_transactions, mock_obj):
        connection_log = ConnectionLog(
            datetime.datetime.now(tz=datetime.timezone.utc),
            datetime.datetime.now(tz=datetime.timezone.utc),
            "dev",
            "awsuser",
            123,
            "app",
            True,
            True,
            "key",
        )
        patched_parse_connections.return_value = [connection_log], 1
        query = Query(
            start_time=datetime.datetime.now(tz=datetime.timezone.utc),
            end_time=datetime.datetime.now(tz=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )
        patched_parse_transactions.return_value = [
            Transaction(
                time_interval=True,
                database_name="dev",
                username="awsuser",
                pid=123,
                xid=345,
                queries=[query],
                transaction_key="dev_awsuser_1073815778",
            )
        ]
        p = ReplayPrep(
            {
                "workload_location": "s3://test-bucket/test-workload-location",
                "time_interval_between_transactions": "true",
                "time_interval_between_queries": "true",
                "filters": [],
            }
        )
        (
            conxn_logs,
            query_count,
            transaction_count,
            first_event_time,
            last_event_time,
            total_connections,
        ) = p.correlate_transactions_with_connections("test-replay")
        self.assertEqual(len(conxn_logs), 1)
        self.assertEqual(conxn_logs[0], connection_log)
        self.assertEqual(query_count, 1)
        self.assertEqual(transaction_count, 1)
        self.assertEqual(total_connections, 1)


if __name__ == "__main__":
    unittest.main()
