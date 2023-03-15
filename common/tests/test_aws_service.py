import datetime
from unittest import TestCase, mock
from unittest.mock import patch, Mock

import boto3
import common.aws_service as aws_service_helper
from botocore.stub import Stubber

redshift_client = boto3.client("redshift", "us-east-1")
cw_client = boto3.client("logs", "us-east-1")
s3_client = boto3.client("s3", "us-east-1")
mock_redshift_client = mock.MagicMock(return_value=redshift_client)
mock_cw_client = mock.MagicMock(return_value=cw_client)
mock_s3_client = mock.MagicMock(return_value=s3_client)


class AWSServiceTestCases(TestCase):
    @patch("boto3.client", mock_redshift_client)
    def test_redshift_describe_logging_status(self):
        s = Stubber(redshift_client)
        s.add_response("describe_logging_status", {})
        s.activate()
        response = aws_service_helper.redshift_describe_logging_status(
            "test.t.us-east-1"
        )
        assert response == {}
        s.deactivate()

    @patch("boto3.client", mock_cw_client)
    def test_cw_describe_log_groups_with_group_name(self):
        s = Stubber(cw_client)
        s.add_response("describe_log_groups", {})
        s.activate()
        response = aws_service_helper.cw_describe_log_groups("test", "us-east-1")
        assert response == {}
        s.deactivate()

    @patch("boto3.client", mock_cw_client)
    def test_cw_describe_log_groups_without_group_name(self):
        s = Stubber(cw_client)
        s.add_response("describe_log_groups", {})
        s.activate()
        response = aws_service_helper.cw_describe_log_groups()
        assert response == {}
        s.deactivate()

    @patch("boto3.client", mock_cw_client)
    def test_cw_describe_log_streams(self):
        s = Stubber(cw_client)
        s.add_response("describe_log_streams", {})
        s.activate()
        response = aws_service_helper.cw_describe_log_streams("test", "us-east-1")
        assert response == {}
        s.deactivate()

    @patch("boto3.client", mock_cw_client)
    def test_cw_get_paginated_logs(self):
        s = Stubber(cw_client)
        s.add_response(
            "filter_log_events", {"nextToken": "abc", "events": [{"message": "ABC"}]}
        )
        s.add_response("filter_log_events", {"events": [{"message": "DEF"}]})
        s.activate()
        response = aws_service_helper.cw_get_paginated_logs(
            "test",
            "test",
            datetime.datetime.fromisoformat("2021-08-15T15:50"),
            datetime.datetime.fromisoformat("2021-08-15T18:55"),
            "us-east-1",
        )
        assert response == ["ABC", "DEF"]
        s.deactivate()

    @patch("boto3.client", mock_s3_client)
    def test_s3_get_bucket_contents(self):
        s = Stubber(s3_client)
        response_with_continuation_token = {
            "Contents": [{}],
            "NextContinuationToken": "ABC",
        }
        response_without_continuation_token = {"Contents": [{}]}
        s.add_response("list_objects_v2", response_with_continuation_token)
        s.add_response("list_objects_v2", response_without_continuation_token)
        s.activate()
        objects = aws_service_helper.s3_get_bucket_contents("bucket", "prefix")
        assert objects == [{}, {}]
