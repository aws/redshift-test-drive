import unittest
from unittest.mock import patch

from core.extract.cloudwatch_extractor import CloudwatchExtractor


def mock_cw_describe_log_groups(region):
    return {"logGroups": [{"logGroupName": "useractivitylog"}]}


def mock_cw_describe_log_streams(log_group_name, region):
    return {"logStreams": [{"logStreamName": "redshift_serverless"}]}


def mock_cw_get_paginated_logs():
    return []


def mock_s3_upload():
    return ""


def mock_parse_log():
    return


class CloudwatchExtractorTestCases(unittest.TestCase):
    @patch("common.aws_service.cw_describe_log_groups", mock_cw_describe_log_groups)
    @patch("common.aws_service.cw_describe_log_streams", mock_cw_describe_log_streams)
    @patch("common.aws_service.cw_get_paginated_logs", mock_cw_get_paginated_logs)
    @patch("common.aws_service.s3_upload", mock_s3_upload)
    @patch("core.extract.extract_parser", mock_parse_log)
    def test_get_extract_from_cw_source_cluster_endpoint_specified(self):
        cw_extractor = CloudwatchExtractor(
            {
                "source_cluster_endpoint": "redshift-serverless.test.us-east-1",
                "workload_location": "s3://test/t",
            }
        )
        cw_extractor.get_extract_from_cloudwatch("2021-08-15T15:50", "2021-08-15T18:55")


if __name__ == "__main__":
    unittest.main()
