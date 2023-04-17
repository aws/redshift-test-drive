import unittest
import boto3
import datetime
from unittest.mock import patch, MagicMock
from unittest import mock, IsolatedAsyncioTestCase
from dateutil.tz import tzutc
from common import aws_service

from tools.ExternalObjectReplicator.util import copy_util


class CopyUtilTestCases(unittest.TestCase):
    @patch("common.aws_service.s3_copy_object")
    def test_copy_parallel(self, mock_s3_copy_object):
        source_location = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "source-test-bucket/call_center.dat.gz",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
            }
        ]
        dest_bucket = "copy_util_test"
        dest_prefix = "copy_files/"
        obj_type = "copyfiles"
        mock_s3_copy_object.return_value = MagicMock({})
        copy_util.copy_parallel(
            source_location=source_location,
            dest_bucket=dest_bucket,
            dest_prefix=dest_prefix,
            obj_type=obj_type,
        )
        self.assertTrue(mock_s3_copy_object.called)
        self.assertEqual(mock_s3_copy_object.call_count, 1)

    @patch("common.aws_service.s3_upload")
    @patch("tools.ExternalObjectReplicator.util.copy_util.copy_parallel")
    def test_clone_s3_objects_not_copy_files(self, mock_s3_upload, mock_copy_parallel):
        target_dest = "simple-replay-test/test"
        obj_type = "test files"
        source_location = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/call_center.dat.gz",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
                "last_modified": datetime.datetime(2019, 10, 8, 12, 5, 6, tzinfo=tzutc()),
            }
        ]
        objects_not_found = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/abcd.parquet",
            }
        ]
        dest_bucket = "copy_util_test"
        dest_prefix = "copy_files/"

        mock_copy_parallel.return_value = {}
        copy_util.clone_objects_to_s3(target_dest, obj_type, source_location, objects_not_found)
        self.assertTrue(mock_s3_upload.called)
        self.assertEqual(mock_s3_upload.call_count, 1)

    @patch("common.aws_service.s3_upload")
    @patch("tools.ExternalObjectReplicator.util.copy_util.copy_parallel")
    def test_clone_s3_objects_copy_files(self, mock_s3_upload, mock_copy_parallel):
        target_dest = "simple-replay-test/test"
        obj_type = "copyfiles"
        source_location = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/call_center.dat.gz",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
                "last_modified": datetime.datetime(2019, 10, 8, 12, 5, 6, tzinfo=tzutc()),
            }
        ]
        objects_not_found = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/abcd.parquet",
            }
        ]
        dest_bucket = "copy_util_test"
        dest_prefix = "copy_files/"

        mock_copy_parallel.return_value = {}
        copy_util.clone_objects_to_s3(target_dest, obj_type, source_location, objects_not_found)
        self.assertTrue(mock_s3_upload.called)
        self.assertEqual(mock_s3_upload.call_count, 1)

    @patch("common.aws_service.s3_upload")
    @patch("tools.ExternalObjectReplicator.util.copy_util.copy_parallel")
    def test_clone_s3_objects_object_found_empty(self, mock_s3_upload, mock_copy_parallel):
        target_dest = "simple-replay-test/test"
        obj_type = "copyfiles"
        source_location = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/call_center.dat.gz",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
                "last_modified": datetime.datetime(2019, 10, 8, 12, 5, 6, tzinfo=tzutc()),
            }
        ]
        objects_not_found = [
            {
                "source_bucket": "",
                "source_key": "",
            }
        ]
        dest_bucket = "copy_util_test"
        dest_prefix = "copy_files/"

        mock_copy_parallel.return_value = {}
        copy_util.clone_objects_to_s3(target_dest, obj_type, source_location, objects_not_found)
        self.assertTrue(mock_s3_upload.called)
        self.assertEqual(mock_s3_upload.call_count, 1)

    def test_get_s3_folder_size(self):
        total_size = "5.36 KB"
        copy_file_list = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/call_center.dat.gz",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
                "last_modified": "",
            },
        ]
        result = copy_util.get_s3_folder_size(copy_file_list=copy_file_list)
        self.assertEqual(result, total_size)
        copy_file_list_with_slash = [
            {
                "source_bucket": "source-test-bucket",
                "source_key": "test/test_data/call_center.dat.gz/",
                "e_tag": '"ee6e0785cb0b431c90d1c006807ae4ee"',
                "size": "5.36 KB",
                "bytes": 5491,
                "last_modified": "",
            },
        ]
        total_size_with_slash = "0.0 Byte"
        result = copy_util.get_s3_folder_size(copy_file_list=copy_file_list_with_slash)
        self.assertEqual(result, total_size_with_slash)

    def test_size_of_data(self):
        actual_kb = copy_util.size_of_data("2345")
        size_kb = "2.29 KB"
        self.assertEqual(actual_kb, size_kb)
        actual_mb = copy_util.size_of_data("23455234")
        size_mb = "22.37 MB"
        self.assertEqual(actual_mb, size_mb)
        actual_gb = copy_util.size_of_data("2345523456")
        size_gb = "2.18 GB"
        self.assertEqual(actual_gb, size_gb)
        actual_tb = copy_util.size_of_data("2345523456234")
        size_tb = "2.13 TB"
        self.assertEqual(actual_tb, size_tb)


class AsyncCopyUtilTestCase(IsolatedAsyncioTestCase):
    @patch("common.aws_service.s3_get_bucket_contents")
    async def test_check_file_existence_object_not_found(self, mock_objects_not_found):
        response = {
            "ColumnMetadata": [{}],
            "Records": [[{"stringValue": "s3://source-test-bucket/test/test_data/file.parquet"}]],
            "TotalNumRows": 1,
            "ResponseMetadata": {},
        }
        obj_type = "copyfiles"
        mock_objects_not_found.return_value = [
            {
                "Key": "test/test_data/file.parquet",
                "LastModified": datetime.datetime(2020, 11, 12, 19, 2, 18, tzinfo=tzutc()),
                "ETag": "abcd567899hkhkjh",
                "Size": 5491,
            }
        ]
        source_location, objects_not_found = await copy_util.check_file_existence(
            response=response, obj_type=obj_type
        )
        self.assertTrue(mock_objects_not_found.called)
        self.assertEqual(mock_objects_not_found.call_count, 1)
        self.assertTrue(source_location[0]["source_key"])
        self.assertFalse(objects_not_found)

    @patch("common.aws_service.s3_get_bucket_contents")
    async def test_check_file_existence_empty_request(self, mock_objects_not_found_empty_req):
        response = {
            "ColumnMetadata": [{}],
            "Records": [
                [
                    {"stringValue": "s3://source-test-bucket/test/test_data/file.parquet"},
                    {"stringValue": "s3://source-test-bucket/test/test_data/file.parquet"},
                ]
            ],
            "TotalNumRows": 1,
            "ResponseMetadata": {},
        }
        obj_type = "notcopyfiles"
        mock_objects_not_found_empty_req.return_value = {}
        source_location, objects_not_found = await copy_util.check_file_existence(
            response=response, obj_type=obj_type
        )
        self.assertTrue(mock_objects_not_found_empty_req.called)
        self.assertEqual(mock_objects_not_found_empty_req.call_count, 1)
        self.assertFalse(mock_objects_not_found_empty_req.return_value)
        self.assertTrue(objects_not_found[0]["source_key"])


if __name__ == "__main__":
    unittest.main()
