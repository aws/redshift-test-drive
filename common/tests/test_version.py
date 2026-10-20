import os
import subprocess
import sys
from unittest import TestCase
from unittest.mock import patch, Mock

import common.util
from common.version import get_version, get_channel, application_name

CHANNEL_ENV = "REDSHIFT_TEST_DRIVE_CLIENT"


def git_result(returncode=0, stdout="c288d94b0f1e2d3c4b5a69788796a5b4c3d2e1f0\n"):
    return Mock(returncode=returncode, stdout=stdout)


class TestVersion(TestCase):
    def setUp(self):
        get_version.cache_clear()
        get_channel.cache_clear()

    def tearDown(self):
        get_version.cache_clear()
        get_channel.cache_clear()

    @patch("subprocess.run", return_value=git_result())
    def test_get_version_short_sha(self, mock_run):
        self.assertEqual(get_version(), "c288d94")
        self.assertEqual(mock_run.call_args.args[0], ["git", "rev-parse", "HEAD"])

    @patch("subprocess.run", return_value=git_result())
    def test_get_version_runs_git_once(self, mock_run):
        get_version()
        get_version()
        self.assertEqual(mock_run.call_count, 1)

    @patch("subprocess.run", side_effect=FileNotFoundError("git"))
    def test_get_version_no_git_binary(self, mock_run):
        self.assertEqual(get_version(), "nogit")

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["git"], 2))
    def test_get_version_timeout(self, mock_run):
        self.assertEqual(get_version(), "nogit")

    @patch("subprocess.run", return_value=git_result(returncode=128, stdout=""))
    def test_get_version_not_a_repository(self, mock_run):
        self.assertEqual(get_version(), "nogit")


class TestChannel(TestCase):
    def setUp(self):
        get_channel.cache_clear()

    def tearDown(self):
        get_channel.cache_clear()

    def test_get_channel_unset(self):
        with patch.dict(os.environ):
            os.environ.pop(CHANNEL_ENV, None)
            self.assertEqual(get_channel(), "cli")

    def test_get_channel_blank(self):
        with patch.dict(os.environ, {CHANNEL_ENV: "  "}):
            self.assertEqual(get_channel(), "cli")

    def test_get_channel_with_version(self):
        with patch.dict(os.environ, {CHANNEL_ENV: "skill/4"}):
            self.assertEqual(get_channel(), "skill/4")

    def test_get_channel_invalid_warns_once(self):
        with patch.dict(os.environ, {CHANNEL_ENV: "bad value!"}):
            with self.assertLogs("WorkloadReplicatorLogger", level="WARNING") as cm:
                self.assertEqual(get_channel(), "cli")
                self.assertEqual(get_channel(), "cli")
            self.assertEqual(len(cm.output), 1)
            self.assertIn("Ignoring invalid REDSHIFT_TEST_DRIVE_CLIENT", cm.output[0])

    @patch("common.version.multiprocessing.parent_process", return_value=Mock())
    def test_get_channel_invalid_silent_in_worker(self, mock_parent):
        with patch.dict(os.environ, {CHANNEL_ENV: "bad value!"}):
            with self.assertNoLogs("WorkloadReplicatorLogger", level="WARNING"):
                self.assertEqual(get_channel(), "cli")

    def test_get_channel_too_many_segments(self):
        with patch.dict(os.environ, {CHANNEL_ENV: "a/b/c"}):
            with self.assertLogs("WorkloadReplicatorLogger", level="WARNING"):
                self.assertEqual(get_channel(), "cli")


class TestApplicationName(TestCase):
    def setUp(self):
        get_version.cache_clear()
        get_channel.cache_clear()

    def tearDown(self):
        get_version.cache_clear()
        get_channel.cache_clear()

    @patch("subprocess.run", return_value=git_result())
    def test_application_name(self, mock_run):
        with patch.dict(os.environ, {CHANNEL_ENV: "skill/4"}):
            self.assertEqual(
                application_name("Replay"), "RedshiftTestDrive-Replay/c288d94/skill/4"
            )

    @patch("redshift_connector.connect")
    def test_db_connect_passes_app_name(self, mock_connect):
        mock_connect.return_value = Mock()
        common.util.db_connect(host="somehost", username="someuser", app_name="x")
        self.assertEqual(mock_connect.call_args.kwargs["application_name"], "x")

    def test_db_connect_odbc_appends_app_name(self):
        mock_pyodbc = Mock()
        with patch.dict(sys.modules, {"pyodbc": mock_pyodbc}):
            common.util.db_connect(
                interface="odbc", host="somehost", odbc_driver="somedriver", app_name="x"
            )
        self.assertTrue(mock_pyodbc.connect.call_args.args[0].endswith("; ApplicationName=x"))
