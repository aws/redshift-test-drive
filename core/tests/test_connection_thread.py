import unittest
from unittest.mock import MagicMock, patch, mock_open, call
from core.replay.connection_thread import ConnectionThread, categorize_error, remove_comments, parse_error
from core.replay.connections_parser import ConnectionLog
from core.replay.transactions_parser import TransactionsParser, Transaction, Query
import common.util
import datetime
import threading


open_mock = mock_open()


def mock_execute_transactions(self,connection):
    return True

def mock_start_time(self):
    return datetime.datetime(2023,2,1,9,45,0,tzinfo=datetime.timezone.utc)

def mock_execute_transaction(self,transaction,connection):
    return True

class TestConnectionThread(unittest.TestCase):

    def setUp(self):
        global connection_log
        global conn_thread
        global transaction
        global config_dict

         
        config_dict ={'tag': '', 'workload_location': 'test-location/Edited_10_Extraction_devsaba-sr-test_2023-01-23T09:46:24.784062+00:00',
                     'target_cluster_endpoint': 'ra3-redshift-cluster-testing.cqm7bdujbnqz.us-east-1.redshift.amazonaws.com:5439/dev',
                        'target_cluster_region': 'us-east-1', 'master_username': 'awsuser', 'nlb_nat_dns': None, 'odbc_driver': None,
                         'default_interface': 'psql', 'time_interval_between_transactions': 'all on', 'time_interval_between_queries': 'all on',
                          'execute_copy_statements': 'false', 'execute_unload_statements': 'false', 'replay_output': 's3://devsaba-sr-drill/replay',
                           'analysis_output': 's3://devsaba-sr-drill/analysis','limit_concurrent_connections':'1','split_multi':'False'}

        connection_log = ConnectionLog(
            session_initiation_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            disconnection_time= datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1),
            application_name='',
            database_name='dev',
            username='awsuser',
            pid='13203827',
            time_interval_between_queries='all on',
            time_interval_between_transactions=True,
            connection_key='dev_awsuser_13203827'
        )

        conn_thread = ConnectionThread(
            process_idx=1,
            job_id=0,
            connection_log=connection_log,
            default_interface="psql",
            odbc_driver=None,
            replay_start= datetime.datetime(2023,2,1,9,45,0,0,tzinfo=datetime.timezone.utc),
            first_event_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            error_logger='',
            thread_stats={'connection_diff_sec': 0, 'transaction_success': 0, 'transaction_error': 0, 'query_success': 0,
                             'query_error': 0, 'connection_error_log': {}, 'transaction_error_log': {}, 'multi_statements': 0, 'executed_queries': 0},
            num_connections=None,
            peak_connections='',
            connection_semaphore=None,
            perf_lock='',
            config=config_dict,
            total_connections='10'
        ) 

        query = [
            Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0'"
                ),
            Query(
                start_time=datetime.datetime(2023, 2, 1, 10, 45, 11, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 45, 21, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
            )
        ]

        transaction = [
            Transaction(
                time_interval=True,
                database_name='dev',
                username='awsuser',
                pid='1073815777',
                xid='272834',
                queries=query,
                transaction_key='dev_awsuser_1073815778'
                        )
        ]

    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_connection_true(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log,mock_time):

        mock_conn = MagicMock()
        mock_conn.close.return_value = True

        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = mock_conn
        mock_offset.return_value = 0.5

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_time.datetime.now.return_value = datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc)

        conn_thread.num_connections = mock_num_connections

        conn_thread.run()

        mock_log.debug.assert_any_call('Establishing connection 1 of 10 at 900.000 (expected: 0.000, +900.000).  Pid: 13203827, Connection times: 2023-02-01 10:00:00+00:00 to 2023-02-01 10:00:01+00:00, 1.0 sec')

    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.datetime')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_connection_false(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_time,mock_log):
        
        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = None
        mock_offset.return_value = 10
        mock_time.datetime.now.return_value = datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc)
        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        conn_thread.num_connections = mock_num_connections

        conn_thread.run()

        mock_log.warning.assert_any_call('Failed to connect')

    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_run_except_clause(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log,mock_time):
        
        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = True
        mock_offset.return_value = 10
        mock_time.datetime.now.return_value = datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc)
        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        conn_thread.run()
        mock_log.error.assert_called()

    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep.get_connection_credentials')
    def test_initiate_connection_along_with_run_test_credentials_except(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log,mock_time):
        
        mock_ReplayPrep.return_value = {'password':'123'}
        mock_dbconnect.side_effect = ImportError
        mock_offset.return_value = 10
        mock_time.datetime.now.return_value = datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc)
        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        conn_thread.run()
        mock_log.error.assert_any_call("(1) Failed to initiate connection for dev-awsuser-13203827 ({'password': '***'}): 'host'")

    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep.get_connection_credentials')
    def test_initiate_connection_along_with_run_test_semaphore_true(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log):

        mock_conn = MagicMock()
        mock_conn.close.return_value = True

        mock_ReplayPrep.return_value = True
        mock_dbconnect.return_value = mock_conn
        mock_offset.return_value = 0.5

        mock_num_connections = MagicMock()
        mock_conn_semaphore = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_conn_semaphore.release.value = True

        conn_thread.connection_semaphore = mock_conn_semaphore
        conn_thread.num_connections = mock_num_connections()

        conn_thread.run()

        mock_log.debug.assert_any_call('Releasing semaphore (0 / 1 active connections)')

    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_application_name_given(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log):

        mock_conn = MagicMock()
        mock_conn.close.return_value = True

        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = mock_conn
        mock_offset.return_value = 0.5

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        conn_thread.run()

        mock_log.debug.assert_any_call('Waiting to disconnect 1.0 sec (pid 13203827)')

    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_application_odbc(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log):

        mock_conn = MagicMock()
        mock_conn.close.return_value = True

        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = mock_conn
        mock_offset.return_value = 0.5

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        connection_log.application_name = 'odbc'
        conn_thread.default_interface = 'odbc'
        conn_thread.odbc_driver = 'odbc'

        conn_thread.run()

        mock_log.debug.assert_any_call('Connected using odbc for PID: 13203827')


    @patch.object(ConnectionThread,'logger')
    @patch('core.replay.connection_thread.current_offset_ms')
    @patch.object(ConnectionThread,'execute_transactions',mock_execute_transactions)
    @patch('core.replay.connection_thread.db_connect')
    @patch('core.replay.connection_thread.ReplayPrep')
    def test_initiate_connection_along_with_run_test_odbc_drive_none(self,mock_ReplayPrep,mock_dbconnect,mock_offset,mock_log):

        mock_conn = MagicMock()
        mock_conn.close.return_value = True

        mock_ReplayPrep.get_connection_credentials.return_value = True
        mock_dbconnect.return_value = mock_conn
        mock_offset.return_value = 0.5

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        connection_log.application_name = 'odbc'
        conn_thread.default_interface = 'odbc'

        conn_thread.run()

        mock_log.warning.assert_any_call("Default driver is set to ODBC. But no ODBC DSN provided. Replay will use PSQL as default driver.")

    @patch.object(Transaction,'start_time')
    @patch.object(ConnectionThread,'execute_transaction',mock_execute_transaction)
    def test_execute_transactions_first_if_in_loop(self,mock_time):

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_time.return_value = datetime.datetime(2023,2,1,10,0,0,10,tzinfo=datetime.timezone.utc)
        connection_log.transactions = transaction

        mock_connection = True

        conn_thread.execute_transactions(mock_connection)

    @patch.object(Transaction,'end_time')
    @patch.object(Transaction,'start_time')
    @patch.object(ConnectionThread,'execute_transaction',mock_execute_transaction)
    def test_execute_transactions_first_else_in_loop(self,mock_start_time,mock_end_time):

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_start_time.return_value = datetime.datetime(2023,2,1,9,45,0, tzinfo=datetime.timezone.utc)
        mock_end_time.return_value = datetime.datetime(2023,2,1,9,50,0, tzinfo=datetime.timezone.utc)
        
        connection_log.transactions = transaction

        mock_connection = True

        conn_thread.execute_transactions(mock_connection)

    @patch.object(Transaction,'end_time')
    @patch.object(Transaction,'start_time')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'execute_transaction',mock_execute_transaction)
    def test_execute_transactions_second_if_in_loop(self,mock_log,mock_start_time,mock_end_time):

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1
        mock_start_time.return_value =  datetime.datetime(2023,2,1,10,0,3,0,tzinfo=datetime.timezone.utc)
        mock_end_time.return_value = datetime.datetime(2023,2,1,10,0,1,0,tzinfo=datetime.timezone.utc)

        query = [
            Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
                ),
            Query(
                start_time=datetime.datetime(2023, 2, 1, 10, 45, 11, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 45, 21, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
            )
        ]

        transaction = [
            Transaction(
                time_interval=True,
                database_name='dev',
                username='awsuser',
                pid='1073815777',
                xid='272834',
                queries=query,
                transaction_key='dev_awsuser_1073815778'
                        ),
            Transaction(
                time_interval=True,
                database_name='dev',
                username='awsuser',
                pid='1073815777',
                xid='272834',
                queries=query,
                transaction_key='dev_awsuser_1073815778'
                        )
        ]

        connection_log = ConnectionLog(
            session_initiation_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            disconnection_time= datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1),
            application_name='odbc',
            database_name='dev',
            username='awsuser',
            pid='13203827',
            time_interval_between_queries='all on',
            time_interval_between_transactions=True,
            connection_key='dev_awsuser_13203827'
        )
        
        connection_log.transactions = transaction


        conn_thread = ConnectionThread(
            process_idx=1,
            job_id=0,
            connection_log=connection_log,
            default_interface="odbc",
            odbc_driver=None,
            replay_start= datetime.datetime(2023,2,1,9,45,0,0,tzinfo=datetime.timezone.utc),
            first_event_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            error_logger='',
            thread_stats={'connection_diff_sec': 0, 'transaction_success': 0, 'transaction_error': 0, 'query_success': 0,
                             'query_error': 0, 'connection_error_log': {}, 'transaction_error_log': {}, 'multi_statements': 0, 'executed_queries': 0},
            num_connections=mock_num_connections,
            peak_connections='',
            connection_semaphore=None,
            perf_lock='',
            config=config_dict,
            total_connections='10'
        )

        mock_connection = True

        conn_thread.execute_transactions(mock_connection)

        mock_log.warning.assert_called()

    @patch.object(ConnectionThread,'execute_transaction',mock_execute_transaction)
    def test_execute_transactions_outer_else(self):

        mock_num_connections = MagicMock()
        mock_num_connections.return_value.value = 1

        query = [
            Query(
            start_time=datetime.datetime(2023, 2, 1, 9, 45, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 9, 45, 10, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
                ),
            Query(
                start_time=datetime.datetime(2023, 2, 1, 9, 45, 11, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 9, 45, 21, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';"
            )
        ]

        transaction = [
            Transaction(
                time_interval=True,
                database_name='dev',
                username='awsuser',
                pid='1073815777',
                xid='272834',
                queries=query,
                transaction_key='dev_awsuser_1073815778'
                        )
        ]

        connection_log = ConnectionLog(
            session_initiation_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            disconnection_time= datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=1),
            application_name='odbc',
            database_name='dev',
            username='awsuser',
            pid='13203827',
            time_interval_between_queries='all on',
            time_interval_between_transactions=False,
            connection_key='dev_awsuser_13203827'
        )
        
        connection_log.transactions = transaction


        conn_thread = ConnectionThread(
            process_idx=1,
            job_id=0,
            connection_log=connection_log,
            default_interface="odbc",
            odbc_driver=None,
            replay_start= datetime.datetime(2023,2,1,9,45,0,0,tzinfo=datetime.timezone.utc),
            first_event_time=datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
            error_logger='',
            thread_stats={'connection_diff_sec': 0, 'transaction_success': 0, 'transaction_error': 0, 'query_success': 0,
                             'query_error': 0, 'connection_error_log': {}, 'transaction_error_log': {}, 'multi_statements': 0, 'executed_queries': 0},
            num_connections=mock_num_connections,
            peak_connections='',
            connection_semaphore=None,
            perf_lock='',
            config=config_dict,
            total_connections='10'
        )

        mock_connection = True

        conn_thread.execute_transactions(mock_connection)

    @patch('core.replay.connection_thread.open',open_mock)
    @patch('core.replay.connection_thread.Path')
    def test_save_query_stats_fp_zero(self,mock_path):

        conn_thread.perf_lock = threading.Lock()
        mock_path.mkdir.return_value = "value"

        conn_thread.save_query_stats(datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
                                     datetime.datetime(2023,2,1,10,0,4,0, tzinfo=datetime.timezone.utc),1,2)

        calls = [call('simplereplay_logs/2023-02-01T09:45:00+00:00/1_times.csv',"a+"),
                 call().__enter__(),
                 call().tell(),
                 call().write('1,1-2,2023-02-01 10:00:00+00:00,2023-02-01 10:00:04+00:00,4.000000,0\n'),
                 call().__exit__(None,None,None)]
        
        open_mock.assert_has_calls(calls, any_order=True)

    @patch('core.replay.connection_thread.open')
    @patch('core.replay.connection_thread.Path')
    def test_save_query_stats_fp_not_zero(self,mock_path,op_mock):

        conn_thread.perf_lock = threading.Lock()
        mock_path.mkdir.return_value = "value"
        mock_fp = MagicMock()
        op_mock.return_value.__enter__.return_value = mock_fp
        mock_fp.tell.return_value = 0

        conn_thread.save_query_stats(datetime.datetime(2023,2,1,10,0,0,0,tzinfo=datetime.timezone.utc),
                                     datetime.datetime(2023,2,1,10,0,4,0, tzinfo=datetime.timezone.utc),1,2)

        calls = [call('simplereplay_logs/2023-02-01T09:45:00+00:00/1_times.csv',"a+"),
                 call().__enter__(),
                 call().__enter__().tell(),
                 call().__enter__().write('# process,query,start_time,end_time,elapsed_sec,rows\n'),
                 call().__enter__().write('1,1-2,2023-02-01 10:00:00+00:00,2023-02-01 10:00:04+00:00,4.000000,0\n'),
                 call().__exit__(None,None,None)]
        op_mock.assert_has_calls(calls, any_order=True)

    
    def test_get_tagged_sql(self):

        value = conn_thread.get_tagged_sql(transaction[0].queries[0].text, conn_thread.process_idx, transaction[0], connection_log)

        self.assertEqual(value,'/* {"xid": "272834", "query_idx": 1, "replay_start": "2023-02-01T09:45:00+00:00"} */ SET query_group=\'0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0\'')
   
    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_with_no_from_s3_or_to_s3(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time):

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.close.return_value = True
        mock_cursor.execute.side_effect = "True"
        mock_connection.commit.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ begin;'
        mock_offset_ms.return_value = 1000.05
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 4

        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';select 1;"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_log.debug.assert_any_call("Executing [SET query_group='0000_create_user.ddl - IR-960eb458-9033-11e...] in 0.0 sec")
        mock_log.debug.assert_any_call('Replayed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1 (4 sec)')

    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_with_invalid_query(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time):

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.close.return_value = True
        mock_cursor.execute.side_effect = "True"
        mock_connection.commit.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ begin;'
        mock_offset_ms.return_value = 1000.05
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 3



        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="select 1 from 's3:test-folder';"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_log.debug.assert_any_call('Replayed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1 (3 sec)')

    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_with_copy_statement_true_from_s3(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time):

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.close.return_value = True
        mock_cursor.execute.side_effect = "True"
        mock_connection.commit.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ select 1 from \'s3:test-folder\''
        mock_offset_ms.return_value = 1000.05
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 2
        conn_thread.config['execute_copy_statements'] = "true"
        


        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="select 1 from 's3:test-folder';"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_log.debug.assert_any_call('Replayed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1 (2 sec)')


    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_with_unload_statement_true_to_s3(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time):

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.close.return_value = True
        mock_cursor.execute.side_effect = "True"
        mock_connection.commit.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ select 1 to \'s3:test-folder\''
        mock_offset_ms.return_value = 1000.05
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 1
        conn_thread.config['execute_unload_statements'] = "true"


        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="select 1 to 's3:test-folder';"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_log.debug.assert_any_call('Replayed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1 (1 sec)')
        self.assertEqual(conn_thread.thread_stats['query_success'], 1)
        self.assertEqual(conn_thread.thread_stats['transaction_success'],1)

    @patch.object(Transaction,'get_base_filename')
    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_with_exception(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time,mock_filename):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.commit.return_value = True
        mock_cursor.execute.side_effect = AttributeError("'bool' object has no attribute 'execute'")
        mock_connection.cursor.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ select 1 to \'s3:test-folder\''
        mock_offset_ms.return_value = 1000.05
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 1
        conn_thread.config['execute_unload_statements'] = "true"
        mock_filename.return_value = 'dev-awsuser-1073815777-272834'


        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="select 1 to 's3:test-folder';"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_log.debug.assert_any_call("Failed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1: 'bool' object has no attribute 'execute'")
        self.assertEqual(conn_thread.thread_stats['query_error'], 1)
        self.assertEqual(conn_thread.thread_stats['transaction_error'],1)
        self.assertEqual(conn_thread.thread_stats['transaction_error_log']['dev-awsuser-1073815777-272834'],[['/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ select 1 to \'s3:test-folder\'', "'bool' object has no attribute 'execute'"]])

    @patch('core.replay.connection_thread.time')
    @patch('core.replay.connection_thread.datetime')
    @patch.object(ConnectionThread,'logger')
    @patch.object(ConnectionThread,'save_query_stats')
    @patch('core.replay.connection_thread.parse_error')
    @patch.object(Query,'offset_ms') 
    @patch.object(ConnectionThread,'get_tagged_sql')
    @patch('core.replay.connection_thread.current_offset_ms')
    def test_execute_transaction_query_execution_multi_statements(self, mock_current_offset_ms,mock_tagged_sql,mock_offset_ms,mock_parse_error,mock_save_stats,mock_log,mock_time,mock_timesleep):

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.close.return_value = True
        mock_connection.close.return_value = True
        mock_cursor.execute.side_effect = "True"
        mock_connection.commit.return_value = mock_cursor
        conn_thread.error_logger = []
        mock_tagged_sql.return_value = '/* {"xid": "272834", "query_idx": 0, "replay_start": "2023-02-01T09:45:00+00:00"} */ begin;'
        mock_offset_ms.return_value = 1011
        mock_current_offset_ms.return_value = 1000
        mock_parse_error.return_value = True
        mock_save_stats.return_value = True
        mock_time.datetime.now().__sub__().total_seconds.return_value = 4
        conn_thread.config['split_multi'] = 'True'


        query_patch = [Query(
            start_time=datetime.datetime(2023, 2, 1, 10, 0, 45,0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2023, 2, 1, 10, 0, 5,0, tzinfo=datetime.timezone.utc),
            text="SET query_group='0000_create_user.ddl - IR-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';select 1;"
                )]
        transaction[0].queries = query_patch
        
        conn_thread.execute_transaction(transaction[0],mock_connection)

        mock_timesleep.sleep.assert_called_once_with(0.011)
        self.assertEqual(transaction[0].queries[0].text,"begin;set query_group='0000_create_user.ddl - ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0';select 1;commit;")
        self.assertEqual(conn_thread.thread_stats['multi_statements'],1)
        self.assertEqual(conn_thread.thread_stats['executed_queries'],4)
        mock_log.debug.assert_any_call('Replayed DB=dev, USER=awsuser, PID=1073815777, XID:272834, Query: 1/1, Multistatement: 4/4 (4 sec)')

class TestCategorizeError(unittest.TestCase):

    def test_categorize_error_with_error(self):

        err_code = '42601'

        value = categorize_error(err_code)
        self.assertEqual(value,"Syntax Error or Access Rule Violation")

    def test_categorize_error_unknown_error(self):

        err_code = '99601'

        value = categorize_error(err_code)
        self.assertEqual(value,"Uncategorized Error")

    
class TestRemoveComments(unittest.TestCase):

    def setUp(self):
        global string
        string = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"
    
    def test_remove_comments(self):
        
        val = remove_comments(string)
        
        self.assertEqual(val,"begin;create  user rsperf password '***' createuser;commit;")


class TestParseError(unittest.TestCase):

    @patch('core.replay.connection_thread.categorize_error')
    @patch('core.replay.connection_thread.remove_comments')
    def test_parse_error(self,mock_query_text,mock_error):

        mock_error.return_value = 'Syntax Error or Access Rule Violation'
        mock_query_text.return_value = "begin;create  user rsperf password '***' createuser;commit;"
        error = "{'S': 'ERROR', 'C': '42601', 'M': 'password must contain at least 8 characters', 'F': '../src/pg/src/backend/commands/user.c', 'L': '146', 'R': 'CheckPasswordFormat'}"
        user = 'awsuser'
        db = 'dev'
        query_text = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"

        err = parse_error(error,user,db,query_text)

        self.assertEqual(err['code'],'42601')
        self.assertEqual(err['message'],'password must contain at least 8 characters')
        self.assertEqual(err['severity'],'ERROR')
        self.assertEqual(err['category'],'Syntax Error or Access Rule Violation')
    
    @patch('core.replay.connection_thread.categorize_error')
    @patch('core.replay.connection_thread.remove_comments')
    def test_parse_error_with_value_D(self,mock_query_text,mock_error):

        mock_error.return_value = 'Syntax Error or Access Rule Violation'
        mock_query_text.return_value = "begin;create  user rsperf password '***' createuser;commit;"
        error = "{'S': 'ERROR', 'C': '42601', 'M': 'password must contain at least 8 characters', 'F': '../src/pg/src/backend/commands/user.c', 'L': '146', 'R': 'CheckPasswordFormat','D':'context:this is a test; query: select 1;'}"
        user = 'awsuser'
        db = 'dev'
        query_text = "begin;create  /* 0000_create_user.ddl.0 !cf:ir-960eb458-9033-11ed-84bb-029845ae12cf.create-user.create-user.s0001.f0000.1.0:cf! */user rsperf password '***' createuser;commit;"

        err = parse_error(error,user,db,query_text)

        self.assertEqual(err['detail'],'this is a test;')