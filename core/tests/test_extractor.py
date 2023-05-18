import datetime
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from core.extract.extractor import Extractor

from core.replay.connections_parser import StartNodeLog


def mock_redshift_describe_logging_status(endpoint):
    if endpoint == "test":
        return {"LoggingEnabled": False}
    elif endpoint == "with_log_destination":
        return {"LoggingEnabled": True, "LogDestinationType": "cloudwatch"}
    elif endpoint == "s3":
        return {"LoggingEnabled": True, "BucketName": "Test", "S3KeyPrefix": "T"}
    else:
        raise RuntimeError


class ExtractorTestCases(unittest.TestCase):
    @patch("core.extract.cloudwatch_extractor")
    def test_cw_extraction_serverless_source_cluster_endpoint(self, mock_cw_extractor):
        e = Extractor(
            {"source_cluster_endpoint": "redshift-serverless"},
            cloudwatch_extractor=mock_cw_extractor,
        )
        e.get_extract("/aws/", "2021-08-15T15:50", "2021-08-15T18:55")
        assert mock_cw_extractor.get_extract_from_cloudwatch.called

    @patch("core.extract.cloudwatch_extractor")
    def test_cw_extraction_log_location_in_config_cloudwatch(self, mock_cw_extractor):
        e = Extractor({"log_location": "/aws/"}, cloudwatch_extractor=mock_cw_extractor)
        e.get_extract("/aws/", "2021-08-15T15:50", "2021-08-15T18:55")
        assert mock_cw_extractor.get_extract_from_cloudwatch.called

    @patch("core.extract.s3_extractor")
    def test_cw_extraction_log_location_interpreted_s3(self, mock_s3_extractor):
        e = Extractor({}, s3_extractor=mock_s3_extractor)
        e.get_extract("s3://bucket/key", "2021-08-15T15:50", "2021-08-15T18:55")
        assert mock_s3_extractor.get_extract_from_s3.called

    @patch("core.extract.cloudwatch_extractor")
    def test_cw_extraction_log_location_interpreted_cloudwatch(self, mock_cw_extractor):
        e = Extractor({}, cloudwatch_extractor=mock_cw_extractor)
        e.get_extract("cloudwatch", "2021-08-15T15:50", "2021-08-15T18:55")
        assert mock_cw_extractor.get_extract_from_cloudwatch.called

    def test_get_parameters_for_log_extraction(self):
        e = Extractor(
            {
                "source_cluster_endpoint": "redshift-serverless.test",
                "start_time": "2022-11-16T00:00:00",
                "end_time": "2022-11-18T00:00:00",
            }
        )

        (
            extraction_name,
            start_time,
            end_time,
            log_location,
        ) = e.get_parameters_for_log_extraction()
        assert log_location == "cloudwatch"

    def test_get_parameters_for_log_extraction_log_location_in_config(self):
        e = Extractor(
            {
                "start_time": "2022-11-16T00:00:00",
                "end_time": "2022-11-18T00:00:00",
                "log_location": "/aws/",
            }
        )
        (
            extraction_name,
            start_time,
            end_time,
            log_location,
        ) = e.get_parameters_for_log_extraction()
        assert log_location == "/aws/"

    @patch(
        "common.aws_service.redshift_describe_logging_status",
        mock_redshift_describe_logging_status,
    )
    def test_get_parameters_for_log_extraction_logging_not_enabled(self):
        e = Extractor(
            {
                "source_cluster_endpoint": "test",
                "start_time": "2022-11-16T00:00:00",
                "end_time": "2022-11-18T00:00:00",
            }
        )
        (
            extraction_name,
            start_time,
            end_time,
            log_location,
        ) = e.get_parameters_for_log_extraction()
        assert log_location is None

    @patch(
        "common.aws_service.redshift_describe_logging_status",
        mock_redshift_describe_logging_status,
    )
    def test_get_parameters_for_log_extraction_logging_in_cloudwatch(self):
        e = Extractor(
            {
                "source_cluster_endpoint": "with_log_destination",
                "start_time": "2022-11-16T00:00:00",
                "end_time": "2022-11-18T00:00:00",
            }
        )
        (
            extraction_name,
            start_time,
            end_time,
            log_location,
        ) = e.get_parameters_for_log_extraction()
        assert log_location == "cloudwatch"

    @patch(
        "common.aws_service.redshift_describe_logging_status",
        mock_redshift_describe_logging_status,
    )
    def test_get_parameters_for_log_extraction_logging_in_s3(self):
        e = Extractor(
            {
                "source_cluster_endpoint": "s3",
                "start_time": "2022-11-16T00:00:00",
                "end_time": "2022-11-18T00:00:00",
            }
        )
        (
            extraction_name,
            start_time,
            end_time,
            log_location,
        ) = e.get_parameters_for_log_extraction()
        assert log_location == "s3://Test/T"

    def test_get_parameters_for_log_extraction_no_log_location_specified(self):
        e = Extractor(
            {"start_time": "2022-11-16T00:00:00", "end_time": "2022-11-18T00:00:00"}
        )
        with self.assertRaises(SystemExit):
            (
                extraction_name,
                start_time,
                end_time,
                log_location,
            ) = e.get_parameters_for_log_extraction()

    def test_get_sql_connections_replacements(self):
        query1 = self.get_query()
        log_items = {"abc.log": [query1]}
        e = Extractor(
            {
                "external_schemas": ["abc_external", "def_schema"],
                "log_location": "test/test_data",
            }
        )
        (
            sql_json,
            missing_conxns,
            replacements,
            statements_to_be_avoided,
        ) = e.get_sql_connections_replacements([], log_items.items())
        assert len(sql_json["transactions"]) > 0
        assert sql_json["transactions"]["123"] is not None
        print(f"{missing_conxns}")

    def get_query(self):
        query1 = StartNodeLog()
        query1.xid = "123"
        query1.pid = "213"
        query1.database_name = "test"
        query1.username = "testuser"
        query1.record_time = datetime.datetime.now()
        query1.text = "select * from test"
        return query1

    def test_validate_log_result(self):
        with self.assertRaises(SystemExit):
            Extractor.validate_log_result([], [])

    @patch("gzip.open", mock_open())
    @patch("builtins.open", mock_open())
    @patch("common.aws_service.s3_upload")
    @patch("common.aws_service.s3_put_object")
    @patch("common.util.cluster_dict")
    @patch.object(Extractor, "get_copy_replacements")
    def test_save_logs_s3(
        self,
        mock_copy_replacements,
        mock_cluster_dict,
        mock_s3_put_object,
        mock_s3_upload,
    ):
        e = Extractor(
            {
                "external_schemas": ["abc_external", "def_schema"],
                "log_location": "test/test_data",
            }
        )
        e.save_logs(
            {"useractivitylog": [self.get_query()]},
            {},
            "s3://test",
            {},
            "2022-11-16T00:00:00",
            "2022-11-18T00:00:00",
        )
        self.assertTrue(mock_s3_upload.called)
        self.assertTrue(mock_s3_put_object.called)

    @patch("gzip.open", mock_open())
    @patch("builtins.open", mock_open())
    @patch("common.util.cluster_dict")
    @patch.object(Extractor, "get_copy_replacements")
    def test_save_logs_non_s3(self, mock_copy_replacements, mock_cluster_dict):
        with patch.object(Path, "mkdir") as mock_mkdir:
            mock_mkdir.return_value = None
            e = Extractor(
                {
                    "external_schemas": ["abc_external", "def_schema"],
                    "source_cluster_endpoint": "source-redshift-test-drive.cqm7bdujbnqz.us-east-1.redshift.amazonaws.com:5439/tpcds_tuned_test",
                    "start_time": "2022-11-16T00:00:00",
                    "end_time": "2022-11-18T00:00:00",
                    "master_username": "awsuser",
                    "region": "us-east-1",
                    "log_location": "test/test_data",
                }
            )
            e.save_logs(
                {"useractivitylog": [self.get_query()]},
                {},
                "/test",
                {},
                "2022-11-16T00:00:00",
                "2022-11-18T00:00:00",
            )
        self.assertTrue(mock_mkdir.called)


if __name__ == "__main__":
    unittest.main()
