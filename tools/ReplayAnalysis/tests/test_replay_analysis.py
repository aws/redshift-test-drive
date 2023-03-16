from unittest.mock import patch, MagicMock, mock_open,Mock
import unittest
import botocore.session
import tools.ReplayAnalysis.replay_analysis as replay_analysis

class TestReplayAnalysis(unittest.TestCase):

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



    @patch('os.system')
    @patch('os.chdir')
    @patch('builtins.print')
    def test_launch_analysis_v2_exit(self, mock_print, mock_chdir, mock_os):
        mock_os.side_effect = [5, 10]
        with self.assertRaises(SystemExit):
            replay_analysis.launch_analysis_v2()
        mock_print.assert_called_once_with("Please install node before proceeding.")

    @patch('os.system')
    @patch('os.chdir')
    @patch('builtins.print')
    def test_launch_analysis_v2_cannot_install(self,mock_print, mock_chdir, mock_os):
        mock_os.side_effect = [0, 0, 1, 1, 1]
        replay_analysis.launch_analysis_v2()
        mock_print.assert_called_once_with("Could not install npm packages. ")

    @patch('os.system', return_value=0)
    @patch('os.chdir')
    @patch('builtins.print')
    def test_launch_analysis_v2_success(self,mock_print, mock_chdir, mock_os):
        replay_analysis.launch_analysis_v2()
        mock_print.assert_not_called()