from unittest.mock import patch, MagicMock, mock_open, Mock
import unittest
import botocore.session
import botocore.errorfactory
import redshift_connector
import botocore.errorfactory
from botocore.exceptions import ClientError
import core.replay.report_gen as report_gen
import pandas

df_mock = pandas.DataFrame(["a", "mock", "for", "test"], columns=['statement_type'])


class TestReportGen(unittest.TestCase):

    def setUp(self):
        self.severless_cluster = {'is_serverless': True, 'secret_name': None, 'host': 'host', 'region': 'someregion',
                                  'port': 5439, 'database': 'somedb', 'id': 'someid'}
        self.bucket = {"url": "someurl", "bucket_name": "somebucket", "prefix": "someprefix"}
        self.provisioned_cluster = {'is_serverless': False, 'secret_name': None, 'host': 'host', 'region': 'someregion',
                                    'port': 5439, 'database': 'somedb', 'id': 'someid'}
        self.report = MagicMock()
        self.replay = "someid"
        self.cluster_endpoint = "someid"
        self.start_time = "sometime"
        self.end_time = "sometime"
        self.bucket_url = "url"
        self.iam_role = "somerole"
        self.user = "someuser"
        self.rs_client_response = {"DbUser": self.user, "DbPassword": "password123"}
        model = botocore.session.get_session().get_service_model('redshift')
        factory = botocore.errorfactory.ClientExceptionsFactory()
        self.exceptions = factory.create_client_exceptions(model)

    @patch("common.util.cluster_dict")
    @patch('common.util.bucket_dict')
    @patch('core.replay.report_gen.unload')
    @patch('core.replay.report_gen.create_json', return_value="fakefile")
    @patch('common.aws_service.s3_upload')
    @patch('core.replay.report_gen.pdf_gen')
    @patch('core.replay.report_gen.analysis_summary')
    def test_replay_pdf_generator_serverless(self, mock_analysis_summary, mock_pdf_gen, mock_upload, mock_create_json,
                                             mock_unload, mock_bucket_dict, mock_cluster_dict):
        mock_cluster_dict.return_value = self.severless_cluster
        mock_bucket_dict.return_value = self.bucket
        report_gen.replay_pdf_generator(self.replay, self.cluster_endpoint, self.start_time, self.end_time,
                                        self.bucket_url, self.iam_role, self.user,
                                        tag='', workload="", is_serverless=True, secret_name=None, nlb_nat_dns=None,
                                        complete=True, stats=None, summary=None)
        self.assertTrue(mock_upload.call_count == 3)
        mock_bucket_dict.assert_called_once_with("url")
        mock_unload.assert_called_once_with(self.bucket,
                                            'somerole', self.severless_cluster,
                                            'someuser', 'someid')
        mock_cluster_dict.assert_called_once_with("someid", True, "sometime", "sometime")
        mock_create_json.assert_called_once_with("someid", self.severless_cluster, '', True, None, '')

    @patch("common.util.cluster_dict")
    @patch('common.util.bucket_dict')
    @patch('core.replay.report_gen.unload', return_value=["query1", "query2"])
    @patch('core.replay.report_gen.create_json')
    @patch('core.replay.report_gen.get_raw_data')
    @patch('core.replay.report_gen.pdf_gen')
    @patch('core.replay.report_gen.analysis_summary')
    @patch('core.replay.report_util.Report')
    @patch('common.aws_service.s3_upload')
    def test_replay_pdf_generator_provisioned(self, mock_upload, mock_report, mock_analysis_summary, mock_pdf_gen,
                                              mock_get_raw_data, mock_create_json, mock_unload, mock_bucket_dict,
                                              mock_cluster_dict):
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        mock_report.return_value = self.report
        report_gen.replay_pdf_generator(self.replay, self.cluster_endpoint, self.start_time, self.end_time,
                                        self.bucket_url, self.iam_role, self.user,
                                        tag='', workload="", is_serverless=False, secret_name=None, nlb_nat_dns=None,
                                        complete=True, stats=None, summary=None)
        mock_bucket_dict.assert_called_once_with("url")
        mock_unload.assert_called_once_with(self.bucket,
                                            'somerole', self.provisioned_cluster,
                                            'someuser', 'someid')
        mock_cluster_dict.assert_called_once_with("someid", False, "sometime", "sometime")
        mock_create_json.assert_called_once_with("someid",
                                                 self.provisioned_cluster,
                                                 '', True, None, '')
        mock_report.assert_called_once_with(self.provisioned_cluster, self.replay, self.bucket,
                                            "someprefixanalysis/someid", "", True)
        mock_get_raw_data.assert_called_with(self.report, self.bucket, "someprefixanalysis/someid", "query2")
        mock_pdf_gen.assert_called_once_with(self.report, None)
        self.assertTrue(mock_upload.call_count == 3)

    @patch("common.util.cluster_dict")
    @patch('common.util.bucket_dict')
    @patch('core.replay.report_gen.unload', return_value=["query1", "query2"])
    @patch('core.replay.report_gen.create_json')
    @patch('core.replay.report_gen.get_raw_data')
    @patch('core.replay.report_gen.pdf_gen')
    @patch('core.replay.report_gen.analysis_summary')
    @patch('core.replay.report_util.Report')
    @patch('common.aws_service.s3_upload')
    def test_replay_pdf_generator_no_key(self, mock_upload, mock_report, mock_analysis_summary, mock_pdf_gen,
                                         mock_get_raw_data, mock_create_json, mock_unload, mock_bucket_dict,
                                         mock_cluster_dict):
        mock_get_raw_data.side_effect = Exception("Boom")
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        with self.assertRaises(SystemExit):
            report_gen.replay_pdf_generator(self.replay, self.cluster_endpoint, self.start_time, self.end_time,
                                            self.bucket_url, self.iam_role, self.user,
                                            tag='', workload="", is_serverless=False, secret_name=None,
                                            nlb_nat_dns=None,
                                            complete=True, stats=None, summary=None)
        mock_pdf_gen.assert_not_called()
        mock_upload.assert_called_once()
        mock_analysis_summary.assert_not_called()

    @patch("common.util.cluster_dict")
    @patch('common.util.bucket_dict')
    @patch('core.replay.report_gen.unload', return_value=["query1", "query2"])
    @patch('core.replay.report_gen.create_json')
    @patch('core.replay.report_gen.get_raw_data')
    @patch('core.replay.report_gen.pdf_gen')
    @patch('core.replay.report_gen.analysis_summary')
    @patch('core.replay.report_util.Report')
    @patch('common.aws_service.s3_upload')
    def test_replay_pdf_generator_client_error(self, mock_upload, mock_report, mock_analysis_summary, mock_pdf_gen,
                                               mock_get_raw_data, mock_create_json, mock_unload, mock_bucket_dict,
                                               mock_cluster_dict):
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        mock_upload.side_effect = [None, ClientError({'Error': {'Code': 'Error!', 'Message': 'oops'}}, 'testing')]
        with self.assertRaises(SystemExit):
            report_gen.replay_pdf_generator(self.replay, self.cluster_endpoint, self.start_time, self.end_time,
                                            self.bucket_url, self.iam_role, self.user,
                                            tag='', workload="", is_serverless=False, secret_name=None,
                                            nlb_nat_dns=None,
                                            complete=True, stats=None, summary=None)

    @patch("common.util.cluster_dict")
    @patch('common.util.bucket_dict')
    @patch('core.replay.report_gen.unload', return_value=["query1", "query2"])
    @patch('core.replay.report_gen.create_json')
    @patch('core.replay.report_util.Report')
    @patch('logging.getLogger')
    @patch('common.aws_service.s3_upload',
           side_effect=ClientError({'Error': {'Code': 'Error!', 'Message': 'oops'}}, 'testing'))
    def test_replay_pdf_generator_cannot_upload(self, mock_upload, mock_logger, mock_report, mock_create_json,
                                                mock_unload, mock_bucket_dict, mock_cluster_dict):
        mock_cluster_dict.return_value = self.provisioned_cluster
        with self.assertRaises(SystemExit):
            report_gen.replay_pdf_generator(self.replay, self.cluster_endpoint, self.start_time, self.end_time,
                                            self.bucket_url, self.iam_role, self.user,
                                            tag='', workload="", is_serverless=True, secret_name=None,
                                            nlb_nat_dns=None,
                                            complete=True, stats=None, summary=None)

    @patch('common.aws_service.s3_client_get_object', return_value={"Body": ""})
    @patch('pandas.read_csv')
    def test_get_raw_data_latency_distribution(self, mock_read_csv, mock_get_object):
        empty_df = pandas.DataFrame()
        mock_report = MagicMock(feature_graph=None)
        mock_read_csv.return_value = empty_df
        report_gen.get_raw_data(mock_report, self.bucket,
                                "some_replay_path", "latency_distribution")
        self.assertTrue(mock_report.feature_graph.empty)
        self.assertTrue(isinstance(mock_report.feature_graph, pandas.DataFrame))

    @patch('common.aws_service.s3_client_get_object', return_value={"Body": ""})
    @patch('pandas.read_csv')
    @patch('core.replay.report_gen.read_data')
    def test_get_raw_data_iterate(self, mock_read_data, mock_read_csv, mock_get_object):
        mock_tables = {1: {"sql": "somesql", "data": "somedata", "columns": "somecolumn", "data": None}}
        empty_df = pandas.DataFrame()
        mock_report = MagicMock(tables=mock_tables)
        mock_read_csv.return_value = empty_df
        report_gen.get_raw_data(mock_report, self.bucket,
                                "some_replay_path", "somesql")
        self.assertTrue(mock_read_data.call_args[0][1].empty)
        self.assertTrue(mock_read_data.call_args[0][0] == 1)
        self.assertTrue(mock_read_data.call_args[0][2] == "somecolumn")
        self.assertTrue(mock_read_data.call_args[0][3] == mock_report)

    @patch('common.aws_service.s3_client_get_object')
    def test_get_raw_data_error(self, mock_get_object):
        mock_get_object.side_effect = Exception("Boom")
        with self.assertRaises(SystemExit):
            report_gen.get_raw_data(self.report, self.bucket,
                                    "some_replay_path", "somesql")

    @patch('common.util.db_connect', return_value=None)
    @patch('logging.getLogger')
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_serverless_success(self, mock_get_creds, get_logger, mock_db_connect):
        mock_get_creds.return_value = {"DbUser": self.user, "DbPassword": "secret_password"}
        with report_gen.initiate_connection(username=self.user, cluster=self.severless_cluster):
            get_logger.assert_called()
            mock_db_connect.assert_called_once_with(host=self.severless_cluster['host'],
                                                    port=self.severless_cluster["port"],
                                                    username="someuser", password="secret_password",
                                                    database=self.severless_cluster['database'])

    @patch('common.aws_service.get_secret',
           return_value={"admin_username": "secret_user", "admin_password": "secret_password"})
    @patch('common.util.db_connect', return_value=None)
    @patch('logging.getLogger')
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_provisioned_success(self, mock_get_cluster_credentials, get_logger,
                                                     mock_db_connect, mock_get_secret):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
            get_logger.assert_called()
            mock_db_connect.assert_called_once_with(host=self.provisioned_cluster['host'],
                                                    port=self.provisioned_cluster["port"],
                                                    username=self.user, password="password123",
                                                    database=self.provisioned_cluster['database'])
            mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")

    @patch('common.aws_service.get_secret',
           return_value={"admin_username": "secret_user", "admin_password": "secret_password"})
    @patch('common.util.db_connect', return_value=None)
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_exception(self, mock_get_cluster_credentials, mock_db_connect,
                                           mock_get_secret):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        mock_db_connect.side_effect = Exception
        with self.assertLogs('SimpleReplayLogger', level='DEBUG') as mock_log:
            with self.assertRaises(SystemExit):
                with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
                    mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")
                    mock_db_connect.assert_called_once_with(host=self.provisioned_cluster['host'],
                                                            port=self.provisioned_cluster["port"],
                                                            username=self.user, password="password123",
                                                            database=self.provisioned_cluster['database'])

    @patch('common.util.db_connect', return_value=None)
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_cluster_not_found(self, mock_get_cluster_credentials, mock_db_connect):
        mock_get_cluster_credentials.side_effect = self.exceptions.ClusterNotFoundFault({}, "")
        with self.assertRaises(SystemExit):
            with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
                mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")
                mock_db_connect.assert_not_called()

    @patch('common.util.db_connect', return_value=None)
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_redshift_conn_error(self, mock_get_cluster_credentials, mock_db_connect):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs('SimpleReplayLogger', level='DEBUG') as mock_log:
            with self.assertRaises(SystemExit):
                with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
                    mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")
                    mock_db_connect.assert_called_once_with(host=self.provisioned_cluster['host'],
                                                            port=self.provisioned_cluster["port"],
                                                            username=self.user, password="password123",
                                                            database=self.provisioned_cluster['database'])

    @patch('common.util.db_connect', return_value=None)
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_no_response(self, mock_get_cluster_credentials, mock_db_connect):
        mock_get_cluster_credentials.return_value = None
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs('SimpleReplayLogger', level='DEBUG') as mock_log:
            with self.assertRaises(SystemExit):
                with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
                    mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")
                    mock_db_connect.assert_not_called()

    @patch('common.util.db_connect', return_value=None)
    @patch('common.aws_service.redshift_get_cluster_credentials')
    def test_initiate_connection_no_password(self, mock_get_cluster_credentials, mock_db_connect):
        mock_get_cluster_credentials.return_value = {"DbUser": self.user, "DbPassword": None}
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs('SimpleReplayLogger', level='DEBUG') as mock_log:
            with self.assertRaises(SystemExit):
                with report_gen.initiate_connection(username=self.user, cluster=self.provisioned_cluster):
                    mock_get_cluster_credentials.assert_called_once_with("someregion", "someuser", "somedb", "someid")
                    mock_db_connect.assert_not_called()
                    self.assertTrue('ERROR:Failed to retrieve credentials for user someuser ' in mock_log.output)

    @patch('os.path.splitext', return_value=["query_name"])
    @patch('os.listdir', return_value=["1.sql", "2.sql", "3.sql"])
    @patch('core.replay.report_gen.initiate_connection', return_value=MagicMock())
    def test_unload_success(self, mock_initiate_connection, mock_listdir, mock_splitext):
        mocked_open = mock_open(read_data="select * from table between {{START_TIME}} and {{END_TIME}}")
        with patch('builtins.open', mocked_open):
            response = report_gen.unload({"url": "someloc"}, "somerole", self.provisioned_cluster,
                                         self.user, self.replay)
            self.assertTrue(response == ["query_name", "query_name", "query_name"])

    @patch('os.path.splitext', return_value=["query_name"])
    @patch('os.listdir', return_value=["1.sql", "2.sql", "3.sql"])
    @patch('core.replay.report_gen.initiate_connection')
    def test_unload_fail(self, mock_init_conn, mock_listdir, mock_splitext):
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = [Exception("boom")]
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_init_conn.return_value.__enter__.return_value = mock_connection
        mocked_open = mock_open(read_data="select * from table between {{START_TIME}} and {{END_TIME}}")
        with self.assertRaises(SystemExit):
            with patch('builtins.open', mocked_open):
                report_gen.unload({"url": "someloc"}, "somerole", self.provisioned_cluster,
                                  self.user, self.replay)

    def test_read_data_empty_df(self):
        with self.assertRaises(SystemExit):
            report_gen.read_data("sometable", pandas.DataFrame(), [], self.report)

    @patch('pandas.DataFrame', return_value=df_mock)
    @patch('common.aws_service.s3_resource_put_object')
    def test_read_data_breakdown(self, mock_s3_put_obj, mock_df):
        mock_tables = {"table_name": {"type": "breakdown"}}
        mock_report = Mock()
        mock_report.tables.return_value = mock_tables
        response = report_gen.read_data("table_name", df_mock, ["Statement Type"], mock_report)
        # assert_frame_equal(response, df_mock)
        self.assertEqual(response["statement_type"][0], "a")
        self.assertEqual(response["statement_type"][1], "mock")
        self.assertEqual(response["statement_type"][3], "test")



    @patch('pandas.DataFrame', return_value=df_mock)
    @patch('common.aws_service.s3_resource_put_object', side_effect=Exception("Boom"))
    def test_read_data_fail(self, mock_s3_put_obj, mock_df):
        mock_tables = {"table_name": {"type": "breakdown"}}
        mock_report = MagicMock(tables=mock_tables)
        with self.assertRaises(SystemExit):
            response = report_gen.read_data("table_name", df_mock, ["Statement Type"], mock_report)

    @patch('common.aws_service.s3_generate_presigned_url')
    def test_create_presigned_url(self, mock_s3_generate_presigned_url):
        report_gen.create_presigned_url("fakebucket", "fakeobject")

        mock_s3_generate_presigned_url.assert_called_once_with(client_method="get_object",
                                                               bucket_name="fakebucket", object_name="fakeobject")

    @patch('common.aws_service.s3_generate_presigned_url')
    def test_create_presigned_url_fail(self, mock_s3_generate_presigned_url):
        mock_s3_generate_presigned_url.side_effect = ClientError({'Error': {'Code':
                                                                                'Error!', 'Message': 'oops'}},
                                                                 'testing')
        response = report_gen.create_presigned_url("fakebucket", "fakeobject")
        self.assertTrue(response == None)

    @patch('core.replay.report_gen.create_presigned_url')
    def test_analysis_summary(self, mock_test_create_presigned_url):
        report_gen.analysis_summary("s3://devsaba-sr-drill/extracts/", "replay_id")

        mock_test_create_presigned_url.called_once_with("devsaba-sr-drill",
                                                        "analysis/replay_id/out/replay_id_report.pdf")


if __name__ == "__main__":
    unittest.main()
