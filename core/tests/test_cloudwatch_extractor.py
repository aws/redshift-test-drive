import unittest
from unittest.mock import patch, mock_open

from core.extract.cloudwatch_extractor import CloudwatchExtractor


def mock_cw_describe_log_groups(log_group_name=None, region=""):
    return {"logGroups": [{"logGroupName": "useractivitylog"}]}


def mock_cw_describe_log_streams(log_group_name, region):
    return {
        "logStreams": [
            {"logStreamName": "redshift-serverless.test.us-east-1"},
        ]
    }


def mock_cw_get_paginated_logs(log_group_name, stream_name, start_time, end_time, region):
    return []


def mock_s3_upload():
    return ""


def mock_parse_log():
    return


class CloudwatchExtractorTestCases(unittest.TestCase):
    @patch("common.aws_service.cw_describe_log_groups", mock_cw_describe_log_groups)
    @patch("common.aws_service.cw_describe_log_streams", mock_cw_describe_log_streams)
    @patch.object(CloudwatchExtractor, "_read_cloudwatch_logs")
    def test_get_extract_from_cw_source_cluster_endpoint_specified(
        self, mock_read_cloudwatch_logs
    ):
        cw_extractor = CloudwatchExtractor(
            {
                "source_cluster_endpoint": "redshift-serverless.test.us-east-1",
                "workload_location": "s3://test/t",
            }
        )
        cw_extractor.get_extract_from_cloudwatch("2021-08-15T15:50", "2021-08-15T18:55")
        mock_read_cloudwatch_logs.assert_called()

    @patch("common.aws_service.cw_describe_log_groups", mock_cw_describe_log_groups)
    @patch("common.aws_service.cw_describe_log_streams", mock_cw_describe_log_streams)
    @patch.object(CloudwatchExtractor, "_read_cloudwatch_logs")
    def test_get_extract_from_cw_source_cluster_endpoint_not_specified(
        self, mock_read_cloudwatch_logs
    ):
        cw_extractor = CloudwatchExtractor({"log_location": "/aws/logs/"})
        cw_extractor.get_extract_from_cloudwatch("2021-08-15T15:50", "2021-08-15T18:55")
        mock_read_cloudwatch_logs.assert_called()

    def test_get_extract_from_cw_error(self):
        cw_extractor = CloudwatchExtractor({})
        with self.assertRaises(SystemExit):
            cw_extractor.get_extract_from_cloudwatch("2021-08-15T15:50", "2021-08-15T18:55")

    @patch("core.extract.cloudwatch_extractor.parse_log")
    @patch("gzip.open", mock_open())
    @patch("tempfile.TemporaryDirectory")
    @patch("common.aws_service.cw_get_paginated_logs", mock_cw_get_paginated_logs)
    @patch("common.aws_service.cw_describe_log_streams", mock_cw_describe_log_streams)
    def test_read_cloudwatch_logs_success(self, mock_tmp_dir, mock_parse_log):
        cw_extractor = CloudwatchExtractor({})
        response = {
            "logGroups": [{"logGroupName": "useractivitylog"}, {"logGroupName": "connectionlog"}]
        }
        cw_extractor._read_cloudwatch_logs(
            response,
            "redshift-serverless.test.us-east-1",
            "2021-08-15T15:50",
            "2021-08-15T18:55",
            "us-east-1",
        )
        self.assertEqual(mock_parse_log.call_count, 2)


if __name__ == "__main__":
    unittest.main()
