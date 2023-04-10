import datetime
import unittest
from unittest.mock import patch, Mock

from core.extract.s3_extractor import S3Extractor


def mock_sync_s3_get_bucket_contents(bucket, prefix):
    return [
        {"Key": "s3://bucket/cluster_connectionlog_2021-08-15T15:00.gz"},
        {"Key": "s3://bucket/cluster_useractivitylog_2021-08-15T19:00.gz"},
    ]


def mock_get_logs_in_range(audit_objects, start_time, end_time):
    return ["A", "B"]


def mock_s3_get_object(bucket, filename):
    mock_obj = Mock()
    mock_obj.get = Mock(return_value={"Body": ""})
    return mock_obj


def mock_parse_log(
    log_file,
    filename,
    connections,
    last_connections,
    logs,
    databases,
    start_time,
    end_time,
):
    return


class S3ExtractorTestCases(unittest.TestCase):
    @patch("core.extract.s3_extractor.get_logs_in_range", mock_get_logs_in_range)
    @patch("common.aws_service.sync_s3_get_bucket_contents", mock_sync_s3_get_bucket_contents)
    @patch("common.aws_service.s3_get_object", mock_s3_get_object)
    @patch("core.extract.extract_parser", mock_parse_log)
    def test_get_extract_from_s3(self):
        s3_extractor = S3Extractor({})
        s3_extractor.get_extract_from_s3(
            "test_bucket",
            "test",
            datetime.datetime.fromisoformat("2021-08-15T15:50").utcoffset(),
            datetime.datetime.fromisoformat("2021-08-15T18:55").utcoffset(),
        )


if __name__ == "__main__":
    unittest.main()
