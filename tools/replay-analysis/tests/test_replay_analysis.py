from unittest.mock import patch, MagicMock, mock_open, Mock
import unittest
import botocore.session
import botocore.errorfactory
import redshift_connector
import botocore.errorfactory
from botocore.exceptions import ClientError
from botocore.stub import Stubber, ANY
from common.aws_service import s3_upload
from util.report_util import Report
from util.report_gen import pdf_gen
import replay_analysis
import pandas
from common.util import (
    db_connect,
    init_logging,
    cluster_dict,
    bucket_dict,
    get_secret,
    create_json,
)


class TestReplayAnalysis(unittest.TestCase):
    def setUp(self):
        self.severless_cluster = {
            "is_serverless": True,
            "secret_name": None,
            "host": "host",
            "region": "someregion",
            "port": 5439,
            "database": "somedb",
            "id": "someid",
        }
        self.bucket = {
            "url": "someurl",
            "bucket_name": "somebucket",
            "prefix": "someprefix",
        }
        self.provisioned_cluster = {
            "is_serverless": False,
            "secret_name": None,
            "host": "host",
            "region": "someregion",
            "port": 5439,
            "database": "somedb",
            "id": "someid",
        }
        self.report = MagicMock()
        self.replay = "someid"
        self.cluster_endpoint = "someid"
        self.start_time = "sometime"
        self.end_time = "sometime"
        self.bucket_url = "url"
        self.iam_role = "somerole"
        self.user = "someuser"
        self.rs_client_response = {"DbUser": self.user, "DbPassword": "password123"}
        model = botocore.session.get_session().get_service_model("redshift")
        factory = botocore.errorfactory.ClientExceptionsFactory()
        self.exceptions = factory.create_client_exceptions(model)

    @patch("os.system")
    @patch("os.chdir")
    @patch("builtins.print")
    def test_launch_analysis_v2_exit(self, mock_print, mock_chdir, mock_os):
        mock_os.side_effect = [5, 10]
        with self.assertRaises(SystemExit):
            replay_analysis.launch_analysis_v2()
        mock_print.assert_called_once_with("Please install node before proceeding.")

    @patch("os.system")
    @patch("os.chdir")
    @patch("builtins.print")
    def test_launch_analysis_v2_cannot_install(self, mock_print, mock_chdir, mock_os):
        mock_os.side_effect = [0, 0, 1, 1, 1]
        replay_analysis.launch_analysis_v2()
        mock_print.assert_called_once_with("Could not install npm packages. ")

    @patch("os.system", return_value=0)
    @patch("os.chdir")
    @patch("builtins.print")
    def test_launch_analysis_v2_success(self, mock_print, mock_chdir, mock_os):
        replay_analysis.launch_analysis_v2()
        mock_print.assert_not_called()

    @patch("util.cluster_dict")
    @patch("util.bucket_dict")
    @patch("replay_analysis.unload")
    @patch("util.create_json", return_value="fakefile")
    @patch("helper.aws_service.s3_upload")
    @patch("report_gen.pdf_gen")
    @patch("replay_analysis.analysis_summary")
    def test_run_replay_analysis_serverless(
        self,
        mock_analysis_summary,
        mock_pdf_gen,
        mock_upload,
        mock_create_json,
        mock_unload,
        mock_bucket_dict,
        mock_cluster_dict,
    ):
        mock_cluster_dict.return_value = self.severless_cluster
        mock_bucket_dict.return_value = self.bucket
        replay_analysis.run_replay_analysis(
            self.replay,
            self.cluster_endpoint,
            self.start_time,
            self.end_time,
            self.bucket_url,
            self.iam_role,
            self.user,
            tag="",
            workload="",
            is_serverless=True,
            secret_name=None,
            nlb_nat_dns=None,
            complete=True,
            stats=None,
            summary=None,
        )
        self.assertTrue(mock_upload.call_count == 3)
        mock_bucket_dict.assert_called_once_with("url")
        mock_unload.assert_called_once_with(
            self.bucket, "somerole", self.severless_cluster, "someuser", "someid"
        )
        mock_cluster_dict.assert_called_once_with(
            "someid", True, "sometime", "sometime"
        )
        mock_create_json.assert_called_once_with(
            "someid", self.severless_cluster, "", True, None, ""
        )

    @patch("util.cluster_dict")
    @patch("util.bucket_dict")
    @patch("replay_analysis.unload", return_value=["query1", "query2"])
    @patch("util.create_json")
    @patch("replay_analysis.get_raw_data")
    @patch("report_gen.pdf_gen")
    @patch("replay_analysis.analysis_summary")
    @patch("report_util.Report")
    @patch("helper.aws_service.s3_upload")
    def test_run_replay_analysis_provisioned(
        self,
        mock_upload,
        mock_report,
        mock_analysis_summary,
        mock_pdf_gen,
        mock_get_raw_data,
        mock_create_json,
        mock_unload,
        mock_bucket_dict,
        mock_cluster_dict,
    ):
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        mock_report.return_value = self.report
        replay_analysis.run_replay_analysis(
            self.replay,
            self.cluster_endpoint,
            self.start_time,
            self.end_time,
            self.bucket_url,
            self.iam_role,
            self.user,
            tag="",
            workload="",
            is_serverless=False,
            secret_name=None,
            nlb_nat_dns=None,
            complete=True,
            stats=None,
            summary=None,
        )
        mock_bucket_dict.assert_called_once_with("url")
        mock_unload.assert_called_once_with(
            self.bucket, "somerole", self.provisioned_cluster, "someuser", "someid"
        )
        mock_cluster_dict.assert_called_once_with(
            "someid", False, "sometime", "sometime"
        )
        mock_create_json.assert_called_once_with(
            "someid", self.provisioned_cluster, "", True, None, ""
        )
        mock_report.assert_called_once_with(
            self.provisioned_cluster,
            self.replay,
            self.bucket,
            "someprefixanalysis/someid",
            "",
            True,
        )
        mock_get_raw_data.assert_called_with(
            self.report, self.bucket, "someprefixanalysis/someid", "query2"
        )
        mock_pdf_gen.assert_called_once_with(self.report, None)
        self.assertTrue(mock_upload.call_count == 3)

    @patch("util.cluster_dict")
    @patch("util.bucket_dict")
    @patch("replay_analysis.unload", return_value=["query1", "query2"])
    @patch("util.create_json")
    @patch("replay_analysis.get_raw_data")
    @patch("report_gen.pdf_gen")
    @patch("replay_analysis.analysis_summary")
    @patch("report_util.Report")
    @patch("helper.aws_service.s3_upload")
    def test_run_replay_analysis_no_key(
        self,
        mock_upload,
        mock_report,
        mock_analysis_summary,
        mock_pdf_gen,
        mock_get_raw_data,
        mock_create_json,
        mock_unload,
        mock_bucket_dict,
        mock_cluster_dict,
    ):
        mock_get_raw_data.side_effect = Exception("Boom")
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        with self.assertRaises(SystemExit):
            replay_analysis.run_replay_analysis(
                self.replay,
                self.cluster_endpoint,
                self.start_time,
                self.end_time,
                self.bucket_url,
                self.iam_role,
                self.user,
                tag="",
                workload="",
                is_serverless=False,
                secret_name=None,
                nlb_nat_dns=None,
                complete=True,
                stats=None,
                summary=None,
            )
        mock_pdf_gen.assert_not_called()
        mock_upload.assert_called_once()
        mock_analysis_summary.assert_not_called()

    @patch("util.cluster_dict")
    @patch("util.bucket_dict")
    @patch("replay_analysis.unload", return_value=["query1", "query2"])
    @patch("util.create_json")
    @patch("replay_analysis.get_raw_data")
    @patch("report_gen.pdf_gen")
    @patch("replay_analysis.analysis_summary")
    @patch("report_util.Report")
    @patch("helper.aws_service.s3_upload")
    def test_run_replay_analysis_client_error(
        self,
        mock_upload,
        mock_report,
        mock_analysis_summary,
        mock_pdf_gen,
        mock_get_raw_data,
        mock_create_json,
        mock_unload,
        mock_bucket_dict,
        mock_cluster_dict,
    ):
        mock_cluster_dict.return_value = self.provisioned_cluster
        mock_bucket_dict.return_value = self.bucket
        mock_upload.side_effect = [
            None,
            ClientError({"Error": {"Code": "Error!", "Message": "oops"}}, "testing"),
        ]
        with self.assertRaises(SystemExit):
            replay_analysis.run_replay_analysis(
                self.replay,
                self.cluster_endpoint,
                self.start_time,
                self.end_time,
                self.bucket_url,
                self.iam_role,
                self.user,
                tag="",
                workload="",
                is_serverless=False,
                secret_name=None,
                nlb_nat_dns=None,
                complete=True,
                stats=None,
                summary=None,
            )

    @patch("util.cluster_dict")
    @patch("util.bucket_dict")
    @patch("replay_analysis.unload", return_value=["query1", "query2"])
    @patch("util.create_json")
    @patch("report_util.Report")
    @patch("logging.getLogger")
    @patch(
        "helper.aws_service.s3_upload",
        side_effect=ClientError(
            {"Error": {"Code": "Error!", "Message": "oops"}}, "testing"
        ),
    )
    def test_run_replay_analysis_cannot_upload(
        self,
        mock_upload,
        mock_logger,
        mock_report,
        mock_create_json,
        mock_unload,
        mock_bucket_dict,
        mock_cluster_dict,
    ):
        mock_cluster_dict.return_value = self.provisioned_cluster
        with self.assertRaises(SystemExit):
            replay_analysis.run_replay_analysis(
                self.replay,
                self.cluster_endpoint,
                self.start_time,
                self.end_time,
                self.bucket_url,
                self.iam_role,
                self.user,
                tag="",
                workload="",
                is_serverless=True,
                secret_name=None,
                nlb_nat_dns=None,
                complete=True,
                stats=None,
                summary=None,
            )

    @patch("helper.aws_service.s3_get_object", return_value={"Body": ""})
    @patch("pandas.read_csv")
    def test_get_raw_data_latency_distribution(self, mock_read_csv, mock_get_object):
        empty_df = pandas.DataFrame()
        mock_report = MagicMock(feature_graph=None)
        mock_read_csv.return_value = empty_df
        replay_analysis.get_raw_data(
            mock_report, self.bucket, "some_replay_path", "latency_distribution"
        )
        self.assertTrue(mock_report.feature_graph.empty)
        self.assertTrue(isinstance(mock_report.feature_graph, pandas.DataFrame))

    @patch("helper.aws_service.s3_get_object", return_value={"Body": ""})
    @patch("pandas.read_csv")
    @patch("replay_analysis.read_data")
    def test_get_raw_data_iterate(self, mock_read_data, mock_read_csv, mock_get_object):
        mock_tables = {
            1: {
                "sql": "somesql",
                "data": "somedata",
                "columns": "somecolumn",
                "data": None,
            }
        }
        empty_df = pandas.DataFrame()
        mock_report = MagicMock(tables=mock_tables)
        mock_read_csv.return_value = empty_df
        replay_analysis.get_raw_data(
            mock_report, self.bucket, "some_replay_path", "somesql"
        )
        self.assertTrue(mock_read_data.call_args[0][1].empty)
        self.assertTrue(mock_read_data.call_args[0][0] == 1)
        self.assertTrue(mock_read_data.call_args[0][2] == "somecolumn")
        self.assertTrue(mock_read_data.call_args[0][3] == mock_report)

    @patch("helper.aws_service.s3_get_object")
    def test_get_raw_data_error(self, mock_get_object):
        mock_get_object.side_effect = Exception("Boom")
        with self.assertRaises(SystemExit):
            replay_analysis.get_raw_data(
                self.report, self.bucket, "some_replay_path", "somesql"
            )

    @patch("builtins.print")
    def test_run_comparison_analysis(self, mock_print):
        replay_analysis.run_comparison_analysis(
            self.bucket["bucket_name"], "somereplay", "somereplay"
        )
        mock_print.assert_called_once_with(
            "Compare replays somereplay and somereplay. Upload to S3 bucket: somebucket."
        )

    @patch("util.db_connect", return_value=None)
    @patch("logging.getLogger")
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_serverless_success(
        self, mock_get_creds, get_logger, mock_db_connect
    ):
        mock_get_creds.return_value = {
            "DbUser": self.user,
            "DbPassword": "secret_password",
        }
        with replay_analysis.initiate_connection(
            username=self.user, cluster=self.severless_cluster
        ):
            get_logger.assert_called()
            mock_db_connect.assert_called_once_with(
                host=self.severless_cluster["host"],
                port=self.severless_cluster["port"],
                username="someuser",
                password="secret_password",
                database=self.severless_cluster["database"],
            )

    @patch(
        "util.get_secret",
        return_value={
            "admin_username": "secret_user",
            "admin_password": "secret_password",
        },
    )
    @patch("util.db_connect", return_value=None)
    @patch("logging.getLogger")
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_provisioned_success(
        self, mock_get_cluster_credentials, get_logger, mock_db_connect, mock_get_secret
    ):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        with replay_analysis.initiate_connection(
            username=self.user, cluster=self.provisioned_cluster
        ):
            get_logger.assert_called()
            mock_db_connect.assert_called_once_with(
                host=self.provisioned_cluster["host"],
                port=self.provisioned_cluster["port"],
                username=self.user,
                password="password123",
                database=self.provisioned_cluster["database"],
            )
            mock_get_cluster_credentials.assert_called_once_with(
                "someregion", "someuser", "somedb", "someid"
            )

    @patch(
        "util.get_secret",
        return_value={
            "admin_username": "secret_user",
            "admin_password": "secret_password",
        },
    )
    @patch("util.db_connect", return_value=None)
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_exception(
        self, mock_get_cluster_credentials, mock_db_connect, mock_get_secret
    ):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        mock_db_connect.side_effect = Exception
        with self.assertLogs("SimpleReplayLogger", level="DEBUG") as mock_log:
            with self.assertRaises(SystemExit):
                with replay_analysis.initiate_connection(
                    username=self.user, cluster=self.provisioned_cluster
                ):
                    mock_get_cluster_credentials.assert_called_once_with(
                        "someregion", "someuser", "somedb", "someid"
                    )
                    mock_db_connect.assert_called_once_with(
                        host=self.provisioned_cluster["host"],
                        port=self.provisioned_cluster["port"],
                        username=self.user,
                        password="password123",
                        database=self.provisioned_cluster["database"],
                    )

    @patch("util.db_connect", return_value=None)
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_cluster_not_found(
        self, mock_get_cluster_credentials, mock_db_connect
    ):
        mock_get_cluster_credentials.side_effect = self.exceptions.ClusterNotFoundFault(
            {}, ""
        )
        with self.assertRaises(SystemExit):
            with replay_analysis.initiate_connection(
                username=self.user, cluster=self.provisioned_cluster
            ):
                mock_get_cluster_credentials.assert_called_once_with(
                    "someregion", "someuser", "somedb", "someid"
                )
                mock_db_connect.assert_not_called()

    @patch("util.db_connect", return_value=None)
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_redshift_conn_error(
        self, mock_get_cluster_credentials, mock_db_connect
    ):
        mock_get_cluster_credentials.return_value = self.rs_client_response
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs("SimpleReplayLogger", level="DEBUG") as mock_log:
            with self.assertRaises(SystemExit):
                with replay_analysis.initiate_connection(
                    username=self.user, cluster=self.provisioned_cluster
                ):
                    mock_get_cluster_credentials.assert_called_once_with(
                        "someregion", "someuser", "somedb", "someid"
                    )
                    mock_db_connect.assert_called_once_with(
                        host=self.provisioned_cluster["host"],
                        port=self.provisioned_cluster["port"],
                        username=self.user,
                        password="password123",
                        database=self.provisioned_cluster["database"],
                    )

    @patch("util.db_connect", return_value=None)
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_no_response(
        self, mock_get_cluster_credentials, mock_db_connect
    ):
        mock_get_cluster_credentials.return_value = None
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs("SimpleReplayLogger", level="DEBUG") as mock_log:
            with self.assertRaises(SystemExit):
                with replay_analysis.initiate_connection(
                    username=self.user, cluster=self.provisioned_cluster
                ):
                    mock_get_cluster_credentials.assert_called_once_with(
                        "someregion", "someuser", "somedb", "someid"
                    )
                    mock_db_connect.assert_not_called()

    @patch("util.db_connect", return_value=None)
    @patch("helper.aws_service.redshift_get_cluster_credentials")
    def test_initiate_connection_no_password(
        self, mock_get_cluster_credentials, mock_db_connect
    ):
        mock_get_cluster_credentials.return_value = {
            "DbUser": self.user,
            "DbPassword": None,
        }
        mock_db_connect.side_effect = redshift_connector.error.Error
        with self.assertLogs("SimpleReplayLogger", level="DEBUG") as mock_log:
            with self.assertRaises(SystemExit):
                with replay_analysis.initiate_connection(
                    username=self.user, cluster=self.provisioned_cluster
                ):
                    mock_get_cluster_credentials.assert_called_once_with(
                        "someregion", "someuser", "somedb", "someid"
                    )
                    mock_db_connect.assert_not_called()
                    self.assertTrue(
                        "ERROR:Failed to retrieve credentials for user someuser "
                        in mock_log.output
                    )

    @patch("os.path.splitext", return_value=["query_name"])
    @patch("os.listdir", return_value=["1.sql", "2.sql", "3.sql"])
    @patch("replay_analysis.initiate_connection", return_value=MagicMock())
    def test_unload_success(
        self, mock_initiate_connection, mock_listdir, mock_splitext
    ):
        mocked_open = mock_open(
            read_data="select * from table between {{START_TIME}} and {{END_TIME}}"
        )
        with patch("builtins.open", mocked_open):
            response = replay_analysis.unload(
                {"url": "someloc"},
                "somerole",
                self.provisioned_cluster,
                self.user,
                self.replay,
            )
            self.assertTrue(response == ["query_name", "query_name", "query_name"])


if __name__ == "__main__":
    unittest.main()
