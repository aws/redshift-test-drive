import datetime
import unittest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from core.extract.extractor import Extractor

from core.replay.connections_parser import Log


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
        query1 = Log()
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

    

if __name__ == "__main__":
    unittest.main()


class TestExtractorEmptyStatements(unittest.TestCase):
    """Entries with no executable statement (e.g. the parser's commented-out repeated
    FETCH lines) must not be written to SQLs.json.gz, and transactions left empty must
    be dropped, so the replay's attempted-query count only holds real statements."""

    def make_query(self, xid, text):
        query = Log()
        query.xid = xid
        query.pid = "213"
        query.database_name = "test"
        query.username = "testuser"
        query.record_time = datetime.datetime.now()
        query.text = text
        return query

    def run_extract(self, queries):
        e = Extractor({"log_location": "test/test_data"})
        sql_json, _, _, _ = e.get_sql_connections_replacements(
            [], {"abc.log": queries}.items()
        )
        return sql_json

    def test_commented_repeated_fetch_is_not_written(self):
        sql_json = self.run_extract(
            [
                self.make_query("1", "FETCH 100 FROM c1;\n"),
                self.make_query("1", "--FETCH 100 FROM c1;\n"),
                self.make_query("1", "--FETCH 100 FROM c1;\n"),
                self.make_query("1", "CLOSE c1;\n"),
            ]
        )
        texts = [q["text"] for q in sql_json["transactions"]["1"]["queries"]]
        self.assertEqual(texts, ["FETCH 100 FROM c1;", "CLOSE c1;"])

    def test_transaction_with_only_empty_statements_is_dropped(self):
        sql_json = self.run_extract(
            [
                self.make_query("1", "select 1;\n"),
                self.make_query("2", "--FETCH 100 FROM c1;\n"),
                self.make_query("2", "-- a stray comment\n"),
            ]
        )
        self.assertEqual(list(sql_json["transactions"].keys()), ["1"])

    def test_statement_with_trailing_comment_is_kept_verbatim(self):
        # The statement is no longer rewritten; the comment stays and the database
        # ignores it. Only the terminating ";" is appended, as for every entry.
        sql_json = self.run_extract(
            [self.make_query("1", "select 1 -- trailing comment\n")]
        )
        texts = [q["text"] for q in sql_json["transactions"]["1"]["queries"]]
        self.assertEqual(texts, ["select 1 -- trailing comment;"])

    def test_dashes_inside_a_string_literal_are_preserved(self):
        # remove_line_comments() would have truncated this to "select 'a;".
        sql_json = self.run_extract(
            [self.make_query("1", "select 'a--b' as x, 'c' as y\n")]
        )
        texts = [q["text"] for q in sql_json["transactions"]["1"]["queries"]]
        self.assertEqual(texts, ["select 'a--b' as x, 'c' as y;"])
