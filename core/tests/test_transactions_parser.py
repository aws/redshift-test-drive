import unittest
import datetime
from dateutil.tz import tzutc
from unittest.mock import patch
from core.replay.transactions_parser import TransactionsParser, Transaction, Query

config = {
    "tag": "",
    "workload_location": "testdata/extract",
    "target_cluster_endpoint": "test.111222333222.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
    "target_cluster_region": "us-east-1",
    "master_username": "testuser",
    "nlb_nat_dns": "",
    "odbc_driver": "",
    "default_interface": "psql",
    "time_interval_between_transactions": "all on",
    "time_interval_between_queries": "all on",
    "execute_copy_statements": "false",
    "execute_unload_statements": "false",
    "replay_output": "s3://location/replay",
    "analysis_output": "",
    "unload_iam_role": "arn:aws:iam::999999999999:role/Test",
    "analysis_iam_role": "",
    "unload_system_table_queries": "unload_system_tables.sql",
    "target_cluster_system_table_unload_iam_role": "",
    "filters": {
        "include": {"database_name": ["*"], "username": ["*"], "pid": ["*"]},
        "exclude": {"database_name": [], "username": [], "pid": []},
    },
}

sql_json = {
    "transactions": {
        "2612671": {
            "xid": "2612671",
            "pid": "1073815778",
            "db": "dev",
            "user": "awsuser",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2023-01-09T15:48:15+00:00",
                    "start_time": None,
                    "end_time": None,
                    "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
                }
            ],
        },
        "2612672": {
            "xid": "2612672",
            "pid": "1073815778",
            "db": "dev",
            "user": "awsuser",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2023-01-09T15:48:15+00:00",
                    "start_time": None,
                    "end_time": None,
                    "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
                }
            ],
        },
    }
}

replay_id = "2023-02-07T19:17:11.472063+00:00_cluster-testing"

transaction_dict = {
    "xid": "2612671",
    "pid": "1073815778",
    "db": "dev",
    "user": "awsuser",
    "time_interval": True,
    "queries": [
        {
            "record_time": "2023-01-09T15:48:15+00:00",
            "start_time": None,
            "end_time": None,
            "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        }
    ],
}


def mock_filters(a, b):
    return True


class TestTransactionParser(unittest.TestCase):
    # need to test more in this function

    @patch("core.replay.transactions_parser.matches_filters", mock_filters)
    @patch.object(Transaction, "start_time")
    @patch.object(TransactionsParser, "parse_transaction")
    @patch("core.replay.transactions_parser.parse_copy_replacements")
    @patch("core.replay.transactions_parser.retrieve_compressed_json")
    def test_parse_transactions_copy_statements_True(
        self, mock_retrieve_json, mock_copy_repl, mock_parse_trans, mock_time
    ):
        config["execute_copy_statements"] = "true"

        q = {
            "record_time": "2023-01-09T15:48:15+00:00",
            "start_time": None,
            "end_time": None,
            "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        }
        transaction_key = "test-key"
        start_time_q = datetime.datetime(2022, 12, 2, 0, 0, 0)
        end_time_q = datetime.datetime(2022, 12, 2, 0, 10, 0)

        mock_time.return_value = True
        queries = Query(start_time_q, end_time_q, q["text"])
        mock_copy_repl.return_value = True
        mock_parse_trans.return_value = Transaction(
            transaction_dict["time_interval"],
            transaction_dict["db"],
            transaction_dict["user"],
            transaction_dict["pid"],
            transaction_dict["xid"],
            queries,
            transaction_key,
        )
        mock_retrieve_json.return_value = sql_json

        parser = TransactionsParser(config, replay_id)

        class_object = parser.parse_transactions()

        mock_copy_repl.assert_called_once_with("testdata/extract")
        mock_retrieve_json.assert_called_once_with("testdata/extract/SQLs.json.gz")
        mock_parse_trans.assert_called_with(
            {
                "xid": "2612672",
                "pid": "1073815778",
                "db": "dev",
                "user": "awsuser",
                "time_interval": True,
                "queries": [
                    {
                        "record_time": "2023-01-09T15:48:15+00:00",
                        "start_time": None,
                        "end_time": None,
                        "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
                    }
                ],
            },
            True,
        )
        assert (
            class_object[0].queries.text
            == "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
        )
        assert class_object[0].pid == "1073815778"

    @patch("core.replay.transactions_parser.matches_filters", mock_filters)
    @patch.object(Transaction, "start_time")
    @patch.object(TransactionsParser, "parse_transaction")
    @patch("core.replay.transactions_parser.parse_copy_replacements")
    @patch("core.replay.transactions_parser.retrieve_compressed_json")
    def test_parse_transactions_copy_statements_False(
        self, mock_retrieve_json, mock_copy_repl, mock_parse_trans, mock_time
    ):
        config["execute_copy_statements"] = "false"

        q = {
            "record_time": "2023-01-09T15:48:15+00:00",
            "start_time": None,
            "end_time": None,
            "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        }
        transaction_key = "test-key"
        start_time = datetime.datetime(2022, 12, 2, 0, 0, 0)
        end_time = datetime.datetime(2022, 12, 2, 0, 10, 0)

        mock_time.return_value = True
        queries = Query(start_time, end_time, q["text"])
        mock_copy_repl.return_value = True
        mock_parse_trans.return_value = Transaction(
            transaction_dict["time_interval"],
            transaction_dict["db"],
            transaction_dict["user"],
            transaction_dict["pid"],
            transaction_dict["xid"],
            queries,
            transaction_key,
        )
        mock_time = True
        mock_retrieve_json.return_value = sql_json

        parser = TransactionsParser(config, replay_id)
        queries = Query(start_time, end_time, q["text"])

        parser.parse_transactions()

        mock_retrieve_json.assert_called_once_with("testdata/extract/SQLs.json.gz")
        mock_parse_trans.assert_called_with(
            {
                "xid": "2612672",
                "pid": "1073815778",
                "db": "dev",
                "user": "awsuser",
                "time_interval": True,
                "queries": [
                    {
                        "record_time": "2023-01-09T15:48:15+00:00",
                        "start_time": None,
                        "end_time": None,
                        "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
                    }
                ],
            },
            [],
        )

    @patch("core.replay.transactions_parser.matches_filters", mock_filters)
    @patch.object(Transaction, "start_time")
    @patch.object(TransactionsParser, "parse_transaction")
    @patch("core.replay.transactions_parser.parse_copy_replacements")
    @patch("core.replay.transactions_parser.retrieve_compressed_json")
    def test_parse_transactions_start_time_false(
        self, mock_retrieve_json, mock_copy_repl, mock_parse_trans, mock_time
    ):
        q = {
            "record_time": "2023-01-09T15:48:15+00:00",
            "start_time": None,
            "end_time": None,
            "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        }
        transaction_key = "test-key"
        start_time = datetime.datetime(2022, 12, 2, 0, 0, 0)
        end_time = datetime.datetime(2022, 12, 2, 0, 10, 0)

        config["execute_copy_statements"] = "false"
        mock_time.return_value = False
        queries = Query(start_time, end_time, q["text"])
        mock_copy_repl.return_value = True
        mock_parse_trans.return_value = Transaction(
            transaction_dict["time_interval"],
            transaction_dict["db"],
            transaction_dict["user"],
            transaction_dict["pid"],
            transaction_dict["xid"],
            queries,
            transaction_key,
        )
        mock_retrieve_json.return_value = sql_json

        parser = TransactionsParser(config, replay_id)
        queries = Query(start_time, end_time, q["text"])

        parser.parse_transactions()

        mock_retrieve_json.assert_called_once_with("testdata/extract/SQLs.json.gz")
        mock_parse_trans.assert_called_with(
            {
                "xid": "2612672",
                "pid": "1073815778",
                "db": "dev",
                "user": "awsuser",
                "time_interval": True,
                "queries": [
                    {
                        "record_time": "2023-01-09T15:48:15+00:00",
                        "start_time": None,
                        "end_time": None,
                        "text": "SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
                    }
                ],
            },
            [],
        )

    @patch("core.replay.transactions_parser.Query")
    def test_parse_transaction_start_time_end_time(self, mock_Query):
        config["execute_copy_statements"] = "false"

        transaction_dict = {
            "xid": "1519323",
            "pid": "1073750303",
            "db": "tpcds_1g",
            "user": "rsperf",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2022-12-27T16:43:34+00:00",
                    "start_time": "2022-12-27T17:00:00+00:00",
                    "end_time": "2022-12-27T17:01:00+00:00",
                    "text": "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';",
                }
            ],
        }

        parser = TransactionsParser(config, replay_id)
        parser.parse_transaction(transaction_dict, None)

        mock_Query.assert_called_once_with(
            datetime.datetime(2022, 12, 27, 17, 0, tzinfo=tzutc()),
            datetime.datetime(2022, 12, 27, 17, 1, tzinfo=tzutc()),
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    @patch.object(TransactionsParser, "get_copy_replacement")
    def test_parse_transaction_copy_statements(self, mock_copy_replacements):
        replacements = {
            "s3://location/catalog_page/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ],
            "s3://location/call_center/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ],
        }

        config["execute_copy_statements"] = "true"

        transaction_dict = {
            "xid": "1519323",
            "pid": "1073750303",
            "db": "tpcds_1g",
            "user": "rsperf",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2022-12-27T16:43:34+00:00",
                    "start_time": None,
                    "end_time": None,
                    "text": "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';",
                }
            ],
        }

        parser = TransactionsParser(config, replay_id)
        parser.parse_transaction(transaction_dict, replacements)

        mock_copy_replacements.assert_called_with(
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';",
            {
                "s3://location/catalog_page/": [
                    "s3://test-location",
                    "arn:iam:role-test-role",
                ],
                "s3://location/call_center/": [
                    "s3://test-location",
                    "arn:iam:role-test-role",
                ],
            },
        )

    @patch("core.replay.transactions_parser.random")
    @patch.object(TransactionsParser, "get_copy_replacement")
    def test_parse_transaction_copy_statements_password(self, mock_copy_replacements, mock_random):
        replacements = {
            "s3://location/catalog_page/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ],
            "s3://location/call_center/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ],
        }

        mock_copy_replacements.return_value = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'arn:iam:role-test-role' \n                region 'us-east-1' \n                gzip delimiter '|';"

        config["execute_copy_statements"] = "true"
        mock_random.choices.return_value = "abcd"

        transaction_dict = {
            "xid": "1519323",
            "pid": "1073750303",
            "db": "tpcds_1g",
            "user": "rsperf",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2022-12-27T16:43:34+00:00",
                    "start_time": None,
                    "end_time": None,
                    "text": "CREATE USER rsperf PASSWORD '***' CREATEUSER;",
                }
            ],
        }

        parser = TransactionsParser(config, replay_id)
        class_object = parser.parse_transaction(transaction_dict, replacements)
        self.assertEqual(
            class_object.queries[0].text,
            "CREATE USER rsperf PASSWORD 'abcdaA0' CREATEUSER;",
        )

    @patch.object(TransactionsParser, "get_unload_replacements")
    def test_parse_transaction_unload_statements(self, mock_unload_replacements):
        config["execute_unload_statements"] = "true"
        config["replay_output"] = "s3://location/replay"
        config["unload_iam_role"] = "arn:aws:iam::111111111111:role/Test"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ]
        }

        transaction_dict = {
            "xid": "1519323",
            "pid": "1073750303",
            "db": "tpcds_1g",
            "user": "rsperf",
            "time_interval": True,
            "queries": [
                {
                    "record_time": "2022-12-27T16:43:34+00:00",
                    "start_time": None,
                    "end_time": None,
                    "text": "unload ('select * from venue') to 's3://mybucket/unload/' iam_role 'arn:aws:iam::0123456789012:role/MyRedshiftRole';",
                }
            ],
        }

        parser = TransactionsParser(config, replay_id)
        parser.parse_transaction(transaction_dict, replacements)

        mock_unload_replacements.assert_called_with(
            "unload ('select * from venue') to 's3://mybucket/unload/' iam_role 'arn:aws:iam::0123456789012:role/MyRedshiftRole';",
            "s3://location/replay",
            "2023-02-07T19:17:11.472063+00:00_cluster-testing",
            "arn:aws:iam::111111111111:role/Test",
        )

    def test_get_unload_replacements_iam_role_with_role(self):
        query_text = "unload ('select * from venue') to 's3://mybucket/unload/' iam_role 'arn:aws:iam::0123456789012:role/MyRedshiftRole';"
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_unload_replacements_credentials(self):
        query_text = "unload ('select * from venue') to 's3://mybucket/unload/' credentials '';"
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_unload_replacements_with_credentials(self):
        query_text = (
            "unload ('select * from venue') to 's3://mybucket/unload/' with credentials as '';"
        )
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_unload_replacements_iam_role(self):
        query_text = "unload ('select * from venue') to 's3://mybucket/unload/' iam_role '';"
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_unload_replacements_with_session_token(self):
        query_text = "unload ('select * from venue') to 's3://mybucket/unload/' access_key_id '' secret_access_key '' session_token '';"
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_unload_replacements_no_session_token(self):
        query_text = "unload ('select * from venue') to 's3://mybucket/unload/' access_key_id '' secret_access_key '';"
        replay_output = config["replay_output"]
        replay_name = replay_id
        unload_iam_role = config["unload_iam_role"]

        parser = TransactionsParser(config, replay_id)

        query = parser.get_unload_replacements(
            query_text, replay_output, replay_name, unload_iam_role
        )
        self.assertEqual(
            query,
            "unload ('select * from venue') to 's3://location/replay/2023-02-07T19:17:11.472063+00:00_cluster-testing/UNLOADs/mybucket/unload/'  IAM_ROLE 'arn:aws:iam::999999999999:role/Test';",
        )

    def test_get_copy_replacement(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';"
        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "arn:iam:role-test-role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'arn:iam:role-test-role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_location(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "",
                "arn:iam:role-test-role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                 IAM_ROLE 'arn:iam:role-test-role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {"": ["", "arn:iam:role-test-role"]}

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(text, None)

    def test_get_copy_replacement_no_copy_replacement(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "",
            ]
        }

        parser = TransactionsParser(config, replay_id)
        with self.assertRaises(SystemExit) as cm:
            text = parser.get_copy_replacement(query_text, replacements)
        self.assertEqual(cm.exception.code, -1)

    def test_get_copy_replacement_no_copy_replacement_iam_role_with_value(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                IAM_ROLE '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_with_credentials(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                with credentials as '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_credentials(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                credentials '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_session_token(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                ACCESS_KEY_ID '' SECRET_ACCESS_KEY '' SESSION_TOKEN '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_access_key(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                ACCESS_KEY_ID '' SECRET_ACCESS_KEY '' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )

    def test_get_copy_replacement_no_copy_replacement_IAM_ROLE(self):
        query_text = "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://location/call_center/'\n                IAM_ROLE 'arn:aws:iam::0123456789012:role/MyRedshiftRole' \n                region 'us-east-1' \n                gzip delimiter '|';"

        replacements = {
            "s3://location/call_center/": [
                "s3://test-location",
                "This_is_a_test_role",
            ]
        }

        parser = TransactionsParser(config, replay_id)

        text = parser.get_copy_replacement(query_text, replacements)

        self.assertEqual(
            text,
            "COPY  /* 0001_01_call_center_copy.sql.0 !CF:IR-fb3d5188-8604-11ed-b844-022e2270cad7.load-tables.load-tables.s0001.f0001.1.1:CF! */public.call_center \n            FROM 's3://test-location'\n                 IAM_ROLE 'This_is_a_test_role' \n                region 'us-east-1' \n                gzip delimiter '|';",
        )
