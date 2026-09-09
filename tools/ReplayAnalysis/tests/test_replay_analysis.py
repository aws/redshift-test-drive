from unittest.mock import patch, MagicMock, mock_open, Mock
import io
import os
import sys
import unittest
import botocore.session
import tools.ReplayAnalysis.replay_analysis as replay_analysis

# The analysis backend runs with the api directory as its working directory, so
# app.py imports its helpers as a top-level "utils" module. Put that directory on
# sys.path so the module can be imported from the test suite as well.
API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

import app as analysis_app  # noqa: E402


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
        self.bucket = {"url": "someurl", "bucket_name": "somebucket", "prefix": "someprefix"}
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


class TestRequestS3Data(unittest.TestCase):
    """Coverage for NULL query_text rows in the unloaded system view data."""

    def setUp(self):
        self.replay = {
            "bucket": "somebucket",
            "s3_prefix": "someprefix/",
            "sid": "A",
            "start_time": "2021-08-15T15:50:09+00:00",
        }
        self.saved_globals = (
            analysis_app.selected_replays,
            analysis_app.boto3_session,
            analysis_app.selected_query_data,
        )
        analysis_app.selected_replays = [self.replay]
        analysis_app.selected_query_data = None

    def tearDown(self):
        (
            analysis_app.selected_replays,
            analysis_app.boto3_session,
            analysis_app.selected_query_data,
        ) = self.saved_globals

    def mock_s3_body(self, csv_text):
        """Serve an in-memory CSV payload to the module's boto3 session."""
        session = MagicMock()
        session.client.return_value.get_object.return_value = {
            "Body": io.BytesIO(csv_text.encode("utf-8"))
        }
        analysis_app.boto3_session = session

    @patch("pandas.DataFrame.to_csv")
    def test_query_history_with_null_query_text(self, mock_to_csv):
        """A NULL query_text must not break the replay_start mask."""
        self.mock_s3_body("query_id,query_text\n1,-- xid: 123 replay_start\n2,\n")

        df = analysis_app.request_s3_data("sys_query_history000", True)

        # The NULL row counts as "no match" and drops out; the replayed statement stays.
        self.assertEqual(1, len(df))
        self.assertEqual([1], df["query_id"].tolist())

    @patch("pandas.DataFrame.to_csv")
    def test_replay_errors_with_null_query_text(self, mock_to_csv):
        """replayerrors000 skips the replay_start filter, so NULLs reach the helpers."""
        self.mock_s3_body("query_text,category\n-- xid: 123 replay_start,Syntax\n,Other\n")

        df = analysis_app.request_s3_data("replayerrors000", False)

        # Both rows survive, and the NULL row reaches the helpers as an empty
        # string instead of a value they cannot handle.
        self.assertEqual(2, len(df))
        self.assertEqual("", df["query_text"].tolist()[-1])
        self.assertEqual(0, df["query_hash"].tolist()[-1])
