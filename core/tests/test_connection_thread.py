import unittest
from random import randint
from unittest.mock import MagicMock, patch, mock_open, call, Mock
from core.replay.connection_thread import (
    ConnectionThread,
    categorize_error,
    remove_comments,
    parse_error,
)
from core.replay.connections_parser import ConnectionLog
from core.replay.transactions_parser import Transaction, Query
import datetime
import threading

config_dict = {
    "tag": "",
    "workload_location": "test-location/Edited_10_Extraction_devsaba-sr-test_2023-01-23T09:46:24.784062+00:00",
    "target_cluster_endpoint": "ra3-redshift-cluster-testing.abc.us-east-1.redshift.amazonaws.com:5439/dev",
    "target_cluster_region": "us-east-1",
    "master_username": "awsuser",
    "nlb_nat_dns": None,
    "odbc_driver": None,
    "default_interface": "psql",
    "time_interval_between_transactions": "all on",
    "time_interval_between_queries": "all on",
    "execute_copy_statements": "false",
    "execute_unload_statements": "false",
    "replay_output": "s3://devsaba-sr-drill/replay",
    "analysis_output": "s3://devsaba-sr-drill/analysis",
    "limit_concurrent_connections": "1",
    "split_multi": "False",
}

query_1 = Query(
    start_time=datetime.datetime(2023, 2, 1, 10, 0, 45, 0, tzinfo=datetime.timezone.utc),
    end_time=datetime.datetime(2023, 2, 1, 10, 0, 45, 0, tzinfo=datetime.timezone.utc),
    text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0'",
)
query_2 = Query(
    start_time=datetime.datetime(2023, 2, 1, 10, 45, 0, tzinfo=datetime.timezone.utc),
    end_time=datetime.datetime(2023, 2, 1, 10, 45, 21, tzinfo=datetime.timezone.utc),
    text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
)
query_3 = Query(
    start_time=datetime.datetime(2023, 2, 1, 9, 45, 0, tzinfo=datetime.timezone.utc),
    end_time=datetime.datetime(2023, 2, 1, 10, 0, 53, 0, tzinfo=datetime.timezone.utc),
    text="select * from user.ddl;",
)


def mock_start_time(self):
    return datetime.datetime(2023, 2, 1, 9, 45, 0, tzinfo=datetime.timezone.utc)


def mock_execute_transaction(self, transaction, connection):
    return True


def mock_date_time():
    mock_time = Mock(
        return_value=datetime.datetime(2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc)
    )
    return mock_time


def get_transactions(queries, xid=str(randint(100000, 999999))):
    transactions = []
    for query in queries:
        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="awsuser",
            pid=str(randint(1000000000, 9999999999)),
            xid=xid,
            queries=queries,
            transaction_key="dev_awsuser_1073815778",
        )
        transactions.append(transaction)
    return transactions


def get_connection_thread(connection_log):
    return ConnectionThread(
        process_idx=1,
        job_id=0,
        connection_log=connection_log,
        default_interface="psql",
        odbc_driver=None,
        replay_start=datetime.datetime(2023, 2, 1, 9, 45, 0, 0, tzinfo=datetime.timezone.utc),
        first_event_time=datetime.datetime(2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc),
        error_logger="",
        thread_stats={
            "connection_diff_sec": 0,
            "transaction_success": 0,
            "transaction_error": 0,
            "query_success": 0,
            "query_error": 0,
            "connection_error_log": {},
            "transaction_error_log": {},
            "multi_statements": 0,
            "executed_queries": 0,
        },
        num_connections=MagicMock(),
        peak_connections="",
        connection_semaphore=Mock(),
        perf_lock="",
        config=config_dict,
        total_connections="10",
    )


def get_connection_log(transactions=[], time_interval_between_transactions=True):
    connection_log = ConnectionLog(
        session_initiation_time=datetime.datetime(
            2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc
        ),
        disconnection_time=datetime.datetime(2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc)
        + datetime.timedelta(seconds=1),
        application_name="",
        database_name="dev",
        username="awsuser",
        pid="13203827",
        time_interval_between_queries="all on",
        time_interval_between_transactions=time_interval_between_transactions,
        connection_key="dev_awsuser_13203827",
    )
    connection_log.transactions = transactions
    return connection_log


class TestConnectionThread(unittest.TestCase):
    @patch("core.replay.connection_thread.current_offset_ms", lambda _: 0.5)
    @patch.object(ConnectionThread, "execute_transactions")
    @patch.object(ConnectionThread, "initiate_connection")
    def test_run_with_connection(self, mock_initiate_connection, mock_execute_transactions):
        mock_conn = MagicMock()
        mock_initiate_connection.return_value.__enter__.return_value = mock_conn
        get_connection_thread(get_connection_log()).run()
        assert mock_execute_transactions.called

    @patch("core.replay.connection_thread.current_offset_ms", lambda _: 0.5)
    @patch.object(ConnectionThread, "execute_transactions")
    @patch.object(ConnectionThread, "initiate_connection")
    def test_run_without_connection(self, mock_initiate_connection, mock_execute_transactions):
        mock_initiate_connection.return_value.__enter__.return_value = None
        get_connection_thread(get_connection_log()).run()
        assert mock_execute_transactions.not_called

    @patch("core.replay.connection_thread.current_offset_ms", lambda _: 0.5)
    @patch.object(ConnectionThread, "initiate_connection")
    def test_run_exception_while_connecting(self, mock_initiate_connection):
        mock_initiate_connection.return_value.__enter__.side_effect = [
            Exception("Failed to connect")
        ]
        with self.assertRaises(SystemExit):
            get_connection_thread(get_connection_log()).run()

    @patch("core.replay.connection_thread.db_connect")
    @patch("core.replay.connection_thread.ReplayPrep")
    def test_initiate_connection_success(self, mock_replay_prep, mock_db_connect):
        mock_replay_prep.get_connection_credentials.return_value = {}
        mock_db_connect.return_value = Mock()
        conn_thread = get_connection_thread(get_connection_log())
        conn_thread.num_connections.return_value.value = 1

        with conn_thread.initiate_connection("Test") as conn:
            c = conn
        self.assertIsNotNone(c)
        assert c.close.called
        assert conn_thread.connection_semaphore.release.called
        self.assertEqual(conn_thread.thread_stats.get("connection_error_log", None), {})

    @patch("core.replay.connection_thread.db_connect")
    @patch("core.replay.connection_thread.ReplayPrep")
    def test_initiate_connection_error_in_db_connect(self, mock_replay_prep, mock_db_connect):
        mock_replay_prep.get_connection_credentials.return_value = {}
        mock_db_connect.side_effect = [Exception("Failed to connect")]
        conn_thread = get_connection_thread(get_connection_log())
        conn_thread.num_connections.return_value.value = 1
        with conn_thread.initiate_connection("Test") as conn:
            c = conn
        self.assertIsNone(c)
        assert conn_thread.connection_semaphore.release.called
        self.assertTrue(len(conn_thread.thread_stats.get("connection_error_log", {})))

    @patch("time.sleep")
    @patch.object(ConnectionThread, "execute_transaction")
    def test_execute_transactions_with_time_interval_between_transactions_with_sleep(
        self, mock_exec_transaction, patched_time_sleep
    ):
        transactions = get_transactions([query_1])
        connection_log = get_connection_log(
            transactions=transactions, time_interval_between_transactions=True
        )
        conn_thread = get_connection_thread(connection_log)
        mock_connection = True
        conn_thread.execute_transactions(mock_connection)
        assert mock_exec_transaction.called_with(transactions, mock_connection)
        patched_time_sleep.assert_called()

    @patch("time.sleep")
    @patch.object(ConnectionThread, "execute_transaction")
    def test_execute_transactions_with_time_interval_between_transactions_without_sleep(
        self, mock_exec_transaction, patched_time_sleep
    ):
        transactions = get_transactions([query_3])
        connection_log = get_connection_log(
            transactions=transactions, time_interval_between_transactions=True
        )
        conn_thread = get_connection_thread(connection_log)
        mock_connection = True
        conn_thread.execute_transactions(mock_connection)
        assert mock_exec_transaction.called_with(transactions, mock_connection)
        patched_time_sleep.assert_not_called()

    @patch("time.sleep")
    @patch.object(Transaction, "end_time")
    @patch.object(Transaction, "start_time")
    @patch.object(ConnectionThread, "execute_transaction")
    def test_execute_transactions_without_time_interval_between_transactions(
        self, mock_exec_transaction, mock_start_time, mock_end_time, patched_time_sleep
    ):
        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_start_time.return_value = datetime.datetime(
            2023, 2, 1, 9, 45, 0, tzinfo=datetime.timezone.utc
        )
        mock_end_time.return_value = datetime.datetime(
            2023, 2, 1, 9, 50, 0, tzinfo=datetime.timezone.utc
        )
        transactions = get_transactions([query_1])

        connection_log = get_connection_log(
            transactions=transactions, time_interval_between_transactions=False
        )
        conn_thread = get_connection_thread(connection_log)

        mock_connection = True
        conn_thread.execute_transactions(mock_connection)
        assert mock_exec_transaction.called_with(transactions, mock_connection)
        patched_time_sleep.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("core.replay.connection_thread.Path")
    def test_save_query_stats_fp_zero(self, mock_path, open_mock):
        conn_thread = get_connection_thread(get_connection_log(get_transactions([query_1])))
        conn_thread.perf_lock = threading.Lock()
        mock_path.mkdir.return_value = "value"

        conn_thread.save_query_stats(
            datetime.datetime(2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2023, 2, 1, 10, 0, 4, 0, tzinfo=datetime.timezone.utc),
            1,
            2,
        )

        calls = [
            call("core/logs/replay/2023-02-01T09:45:00+00:00/1_times.csv", "a+"),
            call().__enter__(),
            call().tell(),
            call().write("1,1-2,2023-02-01 10:00:00+00:00,2023-02-01 10:00:04+00:00,4.000000,0\n"),
            call().__exit__(None, None, None),
        ]

        open_mock.assert_has_calls(calls, any_order=True)

    @patch("core.replay.connection_thread.open", new_callable=mock_open)
    @patch("core.replay.connection_thread.Path")
    def test_save_query_stats_fp_not_zero(self, mock_path, op_mock):
        conn_thread = get_connection_thread(get_connection_log(get_transactions([query_1])))
        conn_thread.perf_lock = threading.Lock()
        mock_path.mkdir.return_value = "value"
        mock_fp = MagicMock()
        op_mock.return_value.__enter__.return_value = mock_fp
        mock_fp.tell.return_value = 0

        conn_thread.save_query_stats(
            datetime.datetime(2023, 2, 1, 10, 0, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2023, 2, 1, 10, 0, 4, 0, tzinfo=datetime.timezone.utc),
            1,
            2,
        )

        calls = [
            call("core/logs/replay/2023-02-01T09:45:00+00:00/1_times.csv", "a+"),
            call().__enter__(),
            call().__enter__().tell(),
            call().__enter__().write("# process,query,start_time,end_time,elapsed_sec,rows\n"),
            call()
            .__enter__()
            .write("1,1-2,2023-02-01 10:00:00+00:00,2023-02-01 10:00:04+00:00,4.000000,0\n"),
            call().__exit__(None, None, None),
        ]
        op_mock.assert_has_calls(calls, any_order=True)

    @patch("time.sleep")
    @patch.object(ConnectionThread, "save_query_stats")
    @patch.object(ConnectionThread, "should_execute_sql", lambda a, b: True)
    def test_execute_transaction_valid_sql_success(
        self, mock_save_query_stats, patched_time_sleep
    ):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        transactions = get_transactions([query_1])
        conn_thread = get_connection_thread(get_connection_log(transactions))

        conn_thread.execute_transaction(transactions[0], mock_connection)
        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called()
        mock_connection.commit.assert_called()
        patched_time_sleep.assert_not_called()
        mock_save_query_stats.assert_called()
        self.assertTrue(conn_thread.thread_stats.get("query_success"))

    @patch("time.sleep")
    @patch.object(ConnectionThread, "save_query_stats")
    @patch.object(ConnectionThread, "should_execute_sql", lambda a, b: False)
    def test_execute_transaction_query_execution_with_invalid_query(
        self, mock_save_query_stats, patched_time_sleep
    ):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        transactions = get_transactions([query_1])
        conn_thread = get_connection_thread(get_connection_log(transactions))

        conn_thread.execute_transaction(transactions[0], mock_connection)

        mock_cursor.execute.assert_not_called()
        mock_cursor.close.assert_called()
        mock_connection.commit.assert_called()
        patched_time_sleep.assert_not_called()
        mock_save_query_stats.assert_called()

    @patch("time.sleep")
    @patch("core.replay.connection_thread.parse_error", lambda a, b, c, d: "Test")
    @patch.object(ConnectionThread, "save_query_stats")
    @patch.object(ConnectionThread, "should_execute_sql", lambda a, b: True)
    def test_execute_transaction_execution_error(self, mock_save_query_stats, patched_time_sleep):
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = [Exception("Failed to execute query")]
        mock_connection.cursor.return_value = mock_cursor

        transactions = get_transactions([query_1])
        conn_thread = get_connection_thread(get_connection_log(transactions))
        conn_thread.error_logger = []

        conn_thread.execute_transaction(transactions[0], mock_connection)

        mock_cursor.close.assert_called()
        mock_connection.commit.assert_called()
        patched_time_sleep.assert_not_called()
        mock_save_query_stats.assert_called()
        self.assertFalse(conn_thread.thread_stats.get("query_success"))

    def test_should_execute_sql_copy_from_s3_in_sql(self):
        connection_thread = get_connection_thread(get_connection_log(get_transactions([query_1])))
        connection_thread.config = {"execute_copy_statements": "true"}
        self.assertTrue(connection_thread.should_execute_sql("copy from 's3://folder'"))
        connection_thread.config = {"execute_copy_statements": "false"}
        self.assertFalse(connection_thread.should_execute_sql("copy from 's3://folder'"))

    def test_should_execute_sql_unload_to_s3_in_sql(self):
        connection_thread = get_connection_thread(get_connection_log(get_transactions([query_1])))
        connection_thread.config = {"execute_unload_statements": "true", "replay_output": "abc"}
        self.assertTrue(connection_thread.should_execute_sql("unload to 's3://folder'"))
        connection_thread.config = {"execute_unload_statements": "false"}
        self.assertFalse(connection_thread.should_execute_sql("unload to 's3://folder'"))


class TestCategorizeError(unittest.TestCase):
    def test_categorize_error_with_error(self):
        err_code = "42601"

        value = categorize_error(err_code)
        self.assertEqual(value, "Syntax Error or Access Rule Violation")

    def test_categorize_error_unknown_error(self):
        err_code = "99601"

        value = categorize_error(err_code)
        self.assertEqual(value, "Uncategorized Error")


class TestRemoveComments(unittest.TestCase):
    def setUp(self):
        global string
        string = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"

    def test_remove_comments(self):
        val = remove_comments(string)

        self.assertEqual(val, "begin;create  user rsperf password '***' createuser;commit;")


class TestParseError(unittest.TestCase):
    @patch("core.replay.connection_thread.categorize_error")
    @patch("core.replay.connection_thread.remove_comments")
    def test_parse_error(self, mock_query_text, mock_error):
        mock_error.return_value = "Syntax Error or Access Rule Violation"
        mock_query_text.return_value = (
            "begin;create  user rsperf password '***' createuser;commit;"
        )
        error = "{'S': 'ERROR', 'C': '42601', 'M': 'password must contain at least 8 characters', 'F': '../src/pg/src/backend/commands/user.c', 'L': '146', 'R': 'CheckPasswordFormat'}"
        user = "awsuser"
        db = "dev"
        query_text = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"

        err = parse_error(error, user, db, query_text)

        self.assertEqual(err["code"], "42601")
        self.assertEqual(err["message"], "password must contain at least 8 characters")
        self.assertEqual(err["severity"], "ERROR")
        self.assertEqual(err["category"], "Syntax Error or Access Rule Violation")

    @patch("core.replay.connection_thread.categorize_error")
    @patch("core.replay.connection_thread.remove_comments")
    def test_parse_error_with_value_D(self, mock_query_text, mock_error):
        mock_error.return_value = "Syntax Error or Access Rule Violation"
        mock_query_text.return_value = (
            "begin;create  user rsperf password '***' createuser;commit;"
        )
        error = "{'S': 'ERROR', 'C': '42601', 'M': 'password must contain at least 8 characters', 'F': '../src/pg/src/backend/commands/user.c', 'L': '146', 'R': 'CheckPasswordFormat','D':'context:this is a test; query: select 1;'}"
        user = "awsuser"
        db = "dev"
        query_text = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"

        err = parse_error(error, user, db, query_text)

        self.assertEqual(err["detail"], "this is a test;")
