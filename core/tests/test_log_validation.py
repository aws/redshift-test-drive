import unittest
from core.util.log_validation import is_duplicate, get_logs_in_range
import os
import datetime
import json
from dateutil.parser import parse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def ts(timestamp_str):
    return parse(timestamp_str).replace(tzinfo=datetime.timezone.utc)


def mock_parse_cloudwatch_logs(start_time, end_time, config):
    return "testCloudwatch"


def mock_get_s3_logs(log_bucket, log_prefix, start_time, end_time):
    return {}, {}, {}, {}


def mock_get_local_logs(log_directory_path, start_time, end_time):
    return {}, {}, {}, {}


class TestIsValidLog(unittest.TestCase):
    def setUp(self):
        pass

    def test_is_duplicate(self):
        query1 = "/*test*/ select 1 "
        query2 = "select 1;"
        query3 = "/*test*/ select 1 "
        query4 = "select /*test*/ 1"
        query5 = "create temp table x"
        query6 = "create temporary table x;"

        self.assertEqual(True, is_duplicate(query1, query3))
        self.assertEqual(False, is_duplicate(query1, query2))
        self.assertEqual(False, is_duplicate(query1, query4))
        self.assertEqual(False, is_duplicate(query2, query4))
        self.assertEqual(True, is_duplicate(query5, query6))


class TestGetLogsInRange(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_logs_in_range_startRangeSpecified(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)
            # start range specified
            files = get_logs_in_range(audit_objects, ts("2021-07-18T00:53"), None)
            self.assertEqual(len(files), len(audit_objects))

    def test_get_logs_in_range_startRangeSpecifiedWithSecondFile(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)
            # start range using second file
            files = get_logs_in_range(audit_objects, ts("2021-07-18T01:53:01"), None)
            self.assertEqual(len(files), len(audit_objects) - 1)
            self.assertEqual(
                files[0],
                "770841116522/longzone-2021-07-19-05-58-48-redshift-team/raw/audit_logs/2021/07/18/770841116522_redshift_us-east-1_longzone_connectionlog_2021-07-18T01:53.gz",
            )

    def test_get_logs_in_range_startRangeSpecifiedUsingLastFile(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)

            # start range using last file
            files = get_logs_in_range(audit_objects, ts("2021-07-20T16:53:01"), None)
            self.assertEqual(len(files), 0)

    def test_get_logs_in_range_bothStartAndEndTimeSpecified(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)
            # both specified
            files = get_logs_in_range(
                audit_objects, ts("2021-07-19T15:50"), ts("2021-07-19T18:55")
            )
            self.assertEqual(len(files), 6)
            self.assertEqual(
                files[0],
                "770841116522/longzone-2021-07-19-05-58-48-redshift-team/raw/audit_logs/2021/07/19/770841116522_redshift_us-east-1_longzone_connectionlog_2021-07-19T14:53.gz",
            )

    def test_get_logs_in_range_beforeRange(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)

            # before range
            files = get_logs_in_range(
                audit_objects, ts("2021-07-15T15:50"), ts("2021-07-15T18:55")
            )
            self.assertEqual(len(files), 0)

    def test_get_logs_in_range_afterRange(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)
            # after range
            files = get_logs_in_range(
                audit_objects, ts("2021-08-15T15:50"), ts("2021-08-15T18:55")
            )
            self.assertEqual(len(files), 0)

    def test_get_logs_in_range_allFilesRead_noTimeRangeSpecified(self):
        with open(
            os.path.join(CURRENT_DIR, "support_files/audit_objects.json"), "r"
        ) as fp:
            audit_objects = json.load(fp)
            # all files read if no time range specified
            files = get_logs_in_range(audit_objects, None, None)
            self.assertEqual(len(files), len(audit_objects))


if __name__ == "__main__":
    unittest.main()
