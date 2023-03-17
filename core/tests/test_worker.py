import unittest
from unittest.mock import patch, MagicMock
from core.replay.worker import ReplayWorker
import datetime
import logging
from core.replay.transactions_parser import Transaction, Query
from core.replay.connections_parser import ConnectionLog
from dateutil.tz import tzutc
from queue import Empty
from core.replay.connection_thread import ConnectionThread
from core.replay.stats import init_stats
import threading


num_connections = MagicMock()
num_connections.return_value.value = 2
peak_connections = 1
connection_semaphore = None
worker_stats = {"connection_diff_sec": float(234584)}
queue = "queue"
first_event_time = datetime.datetime(
    2022, 2, 23, 10, 00, 00, tzinfo=datetime.timezone.utc
)
replay_start_time = datetime.datetime(
    2022, 2, 23, 10, 30, 00, tzinfo=datetime.timezone.utc
)
process_idx = 0
config = {
    "tag": "",
    "workload_location": "test-location/Edited_Extraction_devsaba-sr-test_2023-01-23T09:46:24.784062+00:00",
    "target_cluster_endpoint": "ra3-redshift-cluster-testing.cqm7bdujbnqz.us-east-1.redshift.amazonaws.com:5439/dev",
    "target_cluster_region": "us-east-1",
    "master_username": "awsuser",
    "nlb_nat_dns": None,
    "odbc_driver": None,
    "default_interface": "psql",
    "time_interval_between_transactions": "all on",
    "time_interval_between_queries": "all on",
    "execute_copy_statements": "false",
    "execute_unload_statements": "false",
    "replay_output": None,
    "analysis_output": "test-location",
    "unload_iam_role": "",
    "analysis_iam_role": "",
    "unload_system_table_queries": "unload_system_tables.sql",
    "target_cluster_system_table_unload_iam_role": "",
    "filters": {
        "include": {"database_name": [...], "username": [...], "pid": [...]},
        "exclude": {"database_name": [...], "username": [...], "pid": [...]},
    },
    "log_level": "info",
    "num_workers": None,
    "connection_tolerance_sec": "300",
    "limit_concurrent_connections": "2",
}
total_connections = 1
error_logger = "logger"


def mock_logger():
    logger = logging.getLogger("SimpleReplayWorkerLogger")
    return logger


class TestWorker(unittest.TestCase):
    @patch("core.replay.worker.init_logging")
    def test_replay_init_logging_call(self, mock_init_logging):
        worker = ReplayWorker(
            peak_connections,
            num_connections,
            connection_semaphore,
            worker_stats,
            queue,
            first_event_time,
            replay_start_time,
            process_idx,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_init_logging.assert_called_once_with(
            "replay_worker-1",
            level="info",
            logger_name="SimpleReplayWorkerLogger",
        )

    @patch("core.replay.worker.threading")
    @patch.object(ConnectionLog, "offset_ms")
    @patch("core.replay.worker.datetime")
    @patch("core.replay.worker.init_stats")
    @patch("core.replay.worker.ConnectionThread")
    @patch.object(ReplayWorker, "join_finished_threads")
    @patch.object(ReplayWorker, "logger")
    @patch("core.replay.worker.init_logging")
    def test_replay_job_present(
        self,
        mock_init_logging,
        mock_log,
        mock_finished_thread,
        mock_conn_thread,
        mock_init_stats,
        mock_datetime,
        mock_offset_log,
        mock_thread,
    ):
        mock_queue = MagicMock()
        mock_log.debug.return_value = logging.getLogger("SimpleReplayWorkerLogger")

        mock_init_logging.return_value = True
        mock_finished_thread.return_value = True
        mock_conn_thread.start.return_value = True
        mock_init_stats.return_value = True
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 0, 0, 2)
        mock_thread.current_thread.name.return_value = "0"
        mock_thread.Lock.return_value = True
        mock_thread.enumerate.return_value = [1, 1, 1]
        mock_thread.active_count.return_value = 1

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=1000,
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [{"job_id": 0, "connection": connection}, False]
        replay_start_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
        mock_offset_log.return_value = 3000

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections,
            peak_connections,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_log.debug.assert_any_call(
            "Got job 1, delay +1.000 sec (extracted connection time: 1000)"
        )
        mock_log.debug.assert_any_call(
            "Starting job 1 (extracted connection time: 1000). 3, 1 connections active."
        )
        mock_log.debug.assert_any_call("Got termination signal, finishing up.")
        mock_log.debug.assert_any_call("Waiting for 1 connections to finish...")
        mock_log.debug.assert_any_call(
            "Max connection offset for this process: 234584.000 sec"
        )
        mock_log.debug.assert_any_call("Process 0 finished")

    @patch("core.replay.worker.init_stats")
    @patch("core.replay.worker.ConnectionThread")
    @patch.object(ReplayWorker, "join_finished_threads")
    @patch.object(ReplayWorker, "logger")
    @patch("core.replay.worker.init_logging")
    def test_replay_job_is_False(
        self,
        mock_init_logging,
        mock_log,
        mock_finished_thread,
        mock_conn_thread,
        mock_init_stats,
    ):
        mock_queue = MagicMock()
        mock_log.debug.return_value = logging.getLogger("SimpleReplayWorkerLogger")

        mock_init_logging.return_value = True
        mock_finished_thread.return_value = True
        mock_conn_thread.start.return_value = True
        mock_init_stats.return_value = True

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 313000, tzinfo=datetime.timezone.utc
            ),
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [False]

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections,
            peak_connections,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_log.debug.assert_any_call("Got termination signal, finishing up.")
        mock_log.debug.assert_any_call("Waiting for 0 connections to finish...")

    @patch("core.replay.worker.time")
    @patch("core.replay.worker.threading")
    @patch.object(ConnectionLog, "offset_ms")
    @patch("core.replay.worker.datetime")
    @patch("core.replay.worker.init_stats")
    @patch("core.replay.worker.ConnectionThread")
    @patch.object(ReplayWorker, "join_finished_threads")
    @patch.object(ReplayWorker, "logger")
    @patch("core.replay.worker.init_logging")
    def test_replay_job_present_with_semaphore(
        self,
        mock_init_logging,
        mock_log,
        mock_finished_thread,
        mock_conn_thread,
        mock_init_stats,
        mock_datetime,
        mock_offset_log,
        mock_thread,
        mock_time,
    ):
        mock_queue = MagicMock()
        mock_acquire = MagicMock()
        mock_log.debug.return_value = logging.getLogger("SimpleReplayWorkerLogger")

        mock_init_logging.return_value = True
        mock_finished_thread.return_value = True
        mock_conn_thread.start.return_value = True
        mock_init_stats.return_value = True
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 0, 0, 2)
        mock_thread.current_thread.name.return_value = "0"
        mock_thread.Lock.return_value = True
        mock_thread.enumerate.return_value = [1, 1, 1]
        mock_thread.active_count.return_value = 1
        mock_time.time.return_value = 10
        mock_acquire.acquire.return_value = True

        connection_semaphore = mock_acquire

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=1000,
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [{"job_id": 0, "connection": connection}, False]
        replay_start_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
        mock_offset_log.return_value = 3000

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections(),
            peak_connections,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_log.debug.assert_any_call(
            "Checking for connection throttling (2 / 2 active connections)"
        )
        mock_log.debug.assert_any_call("Waited 0 sec for semaphore")

    @patch("core.replay.worker.time")
    @patch("core.replay.worker.threading")
    @patch.object(ConnectionLog, "offset_ms")
    @patch("core.replay.worker.datetime")
    @patch("core.replay.worker.init_stats")
    @patch("core.replay.worker.ConnectionThread")
    @patch.object(ReplayWorker, "join_finished_threads")
    @patch.object(ReplayWorker, "logger")
    @patch("core.replay.worker.init_logging")
    def test_replay_job_Empty(
        self,
        mock_init_logging,
        mock_log,
        mock_finished_thread,
        mock_conn_thread,
        mock_init_stats,
        mock_datetime,
        mock_offset_log,
        mock_thread,
        mock_time,
    ):
        mock_queue = MagicMock()
        mock_log.debug.return_value = logging.getLogger("SimpleReplayWorkerLogger")

        mock_init_logging.return_value = True
        mock_finished_thread.return_value = True
        mock_conn_thread.start.return_value = True
        mock_init_stats.return_value = True
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 0, 0, 2)
        mock_thread.current_thread.name.return_value = "0"
        mock_thread.Lock.return_value = True
        mock_thread.enumerate.return_value = [1, 1, 1]
        mock_thread.active_count.return_value = 1
        mock_time.time.side_effect = [200, 400]

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=1000,
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [Empty, Empty, False]
        replay_start_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
        mock_offset_log.return_value = 3000

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections,
            peak_connections,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_log.debug.assert_any_call("No jobs for 10 seconds (timeout 120)")
        mock_log.warning.assert_any_call("Queue empty for 210 sec, exiting")

    @patch("core.replay.worker.threading")
    @patch.object(ConnectionLog, "offset_ms")
    @patch("core.replay.worker.datetime")
    @patch("core.replay.worker.init_stats")
    @patch("core.replay.worker.ConnectionThread")
    @patch.object(ReplayWorker, "join_finished_threads")
    @patch.object(ReplayWorker, "logger")
    @patch("core.replay.worker.init_logging")
    def test_replay_job_exception(
        self,
        mock_init_logging,
        mock_log,
        mock_finished_thread,
        mock_conn_thread,
        mock_init_stats,
        mock_datetime,
        mock_offset_log,
        mock_thread,
    ):
        mock_queue = MagicMock()
        mock_log.debug.return_value = logging.getLogger("SimpleReplayWorkerLogger")

        mock_init_logging.return_value = True
        mock_finished_thread.return_value = True
        mock_conn_thread.start.return_value = True
        mock_init_stats.return_value = True
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 0, 0, 2)
        mock_thread.current_thread.name.return_value = "0"
        mock_thread.Lock.return_value = True
        mock_thread.enumerate.return_value = [1, 1, 1]
        mock_thread.active_count.return_value = 1

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=1000,
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [{"job_id": 0, "connection": connection}, False]
        replay_start_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
        mock_offset_log.return_value = datetime.datetime(2023, 1, 1, 0, 2, 0)

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections,
            peak_connections,
            config,
            total_connections,
            error_logger,
        )

        worker.replay()

        mock_log.error.assert_called()
        mock_log.debug.assert_called()

    @patch("core.replay.worker.collect_stats")
    def test_join_finished_threads(self, mock_stats):
        mock_queue = MagicMock()
        mock_connection_thread = MagicMock()

        mock_connection_thread.is_alive.return_value = False
        mock_connection_thread.join.return_value = True

        query = Query(
            start_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            end_time=datetime.datetime(2023, 1, 9, 15, 48, 15, tzinfo=tzutc()),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';",
        )

        transaction = Transaction(
            time_interval=True,
            database_name="dev",
            username="testuser",
            pid="1073815778",
            xid="2612671",
            queries=query,
            transaction_key="dev_testuser_1073815778",
        )

        connection = ConnectionLog(
            session_initiation_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 313000, tzinfo=datetime.timezone.utc
            ),
            disconnection_time=datetime.datetime(
                2023, 1, 9, 15, 48, 15, 872000, tzinfo=datetime.timezone.utc
            ),
            application_name="",
            database_name="dev",
            username="testuser",
            pid="1073815778",
            time_interval_between_transactions=True,
            time_interval_between_queries="all on",
            connection_key="dev_testuser_1073815778",
        )

        connection.transactions = transaction

        mock_queue.get.side_effect = [{"job_id": 0, "connection": connection}, False]
        replay_start_time = datetime.datetime(
            2023, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )

        worker = ReplayWorker(
            process_idx,
            replay_start_time,
            first_event_time,
            mock_queue,
            worker_stats,
            connection_semaphore,
            num_connections,
            peak_connections,
            config,
            total_connections,
            error_logger,
        )
        connection_threads = {}
        thread_stats = init_stats({})
        connection_thread = ConnectionThread(
            process_idx=process_idx,
            job_id=0,
            connection_log=connection,
            default_interface=config["default_interface"],
            odbc_driver=config["odbc_driver"],
            replay_start=replay_start_time,
            first_event_time=first_event_time,
            error_logger=error_logger,
            thread_stats=0,
            num_connections=num_connections,
            peak_connections=peak_connections,
            connection_semaphore=connection_semaphore,
            perf_lock=threading.Lock(),
            config=config,
            total_connections=total_connections,
        )
        connection_thread.start()
        connection_threads[mock_connection_thread] = thread_stats

        length = worker.join_finished_threads(
            connection_threads=connection_threads, worker_stats=worker_stats
        )

        mock_stats.assert_called_once_with(
            {"connection_diff_sec": 234584.0},
            {
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
        )
        self.assertEqual(length, 1)
