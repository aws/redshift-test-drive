import unittest
from unittest.mock import patch, Mock
import sys

from moto.glue.exceptions import DatabaseNotFoundException, TableNotFoundException

from tools.ExternalObjectReplicator.util import glue_util


def mock_glue_get_database(name, region):
    return {}


def mock_create_database(name, message, region):
    return {}


def mock_glue_get_table(database="test", table="test", region="us-east-1"):
    return {
        "Table": {
            "Name": "Test",
            "PartitionKeys": "ABC",
            "StorageDescriptor": {
                "Location": "s3://test-location/test-key",
                "Columns": ["A", "B", "C"],
            },
        }
    }


def mock_glue_get_partition_indexes(database, table, region):
    return {"PartitionIndexDescriptorList"}


def mock_glue_create_table(database, table_input, region):
    return {}


class GlueUtilTestCases(unittest.TestCase):
    @patch("common.aws_service.glue_get_database", mock_glue_get_database)
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch("common.aws_service.glue_get_table", mock_glue_get_table)
    @patch("common.aws_service.glue_create_table", mock_glue_create_table)
    @patch("common.aws_service.glue_get_partition_indexes", mock_glue_get_partition_indexes)
    def test_glue_cloning(self):
        response = glue_util.clone_glue_catalog(
            records=[
                [
                    {"stringValue": "simple_replay"},
                    {"stringValue": "simple_replay_test_database"},
                    {"stringValue": "sales_data_table"},
                    {"stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"},
                ]
            ],
            dest_location="s3://simple-replay-test/test",
            region="us-east-1",
        )
        self.assertTrue(response)

    @patch("common.aws_service.glue_get_database", Mock(side_effect=[Exception()]))
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch("common.aws_service.glue_get_table", mock_glue_get_table)
    @patch("common.aws_service.glue_create_table", mock_glue_create_table)
    @patch("common.aws_service.glue_get_partition_indexes", mock_glue_get_partition_indexes)
    def test_glue_cloning_with_exception(self):
        with self.assertRaises(SystemExit):
            glue_util.clone_glue_catalog(
                records=[
                    [
                        {"stringValue": "simple_replay"},
                        {"stringValue": "simple_replay_test_database"},
                        {"stringValue": "sales_data_table"},
                        {
                            "stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"
                        },
                    ]
                ],
                dest_location="s3://simple-replay-test/test",
                region="us-east-1",
            )

    @patch(
        "common.aws_service.glue_get_database",
        Mock(side_effect=[DatabaseNotFoundException("test")]),
    )
    @patch("common.aws_service.glue_create_database")
    @patch("common.aws_service.glue_get_table", mock_glue_get_table)
    @patch("common.aws_service.glue_create_table", mock_glue_create_table)
    @patch("common.aws_service.glue_get_partition_indexes", mock_glue_get_partition_indexes)
    def test_glue_cloning_with_database_not_found_exception(self, mock_create_database):
        glue_util.clone_glue_catalog(
            records=[
                [
                    {"stringValue": "simple_replay"},
                    {"stringValue": "simple_replay_test_database"},
                    {"stringValue": "sales_data_table"},
                    {"stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"},
                ]
            ],
            dest_location="s3://simple-replay-test/test",
            region="us-east-1",
        )
        mock_create_database.assert_called()

    @patch("common.aws_service.glue_get_database", mock_glue_get_database)
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch("common.aws_service.glue_get_table", Mock(side_effect=[Exception()]))
    @patch("common.aws_service.glue_create_table", mock_glue_create_table)
    @patch("common.aws_service.glue_get_partition_indexes", mock_glue_get_partition_indexes)
    def test_glue_cloning_exception_in_table_copy(self):
        with self.assertRaises(SystemExit):
            glue_util.clone_glue_catalog(
                records=[
                    [
                        {"stringValue": "simple_replay"},
                        {"stringValue": "simple_replay_test_database"},
                        {"stringValue": "sales_data_table"},
                        {
                            "stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"
                        },
                    ]
                ],
                dest_location="s3://simple-replay-test/test",
                region="us-east-1",
            )

    @patch("common.aws_service.glue_get_database", mock_glue_get_database)
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch(
        "common.aws_service.glue_get_table",
        Mock(side_effect=[TableNotFoundException("table"), mock_glue_get_table()]),
    )
    @patch("common.aws_service.glue_create_table")
    @patch(
        "common.aws_service.glue_get_partition_indexes",
        Mock(return_value={"PartitionIndexDescriptorList": "Test"}),
    )
    def test_glue_cloning_table_not_found_in_table_copy(self, mock_create_table):
        glue_util.clone_glue_catalog(
            records=[
                [
                    {"stringValue": "simple_replay"},
                    {"stringValue": "simple_replay_test_database"},
                    {"stringValue": "sales_data_table"},
                    {"stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"},
                ]
            ],
            dest_location="s3://simple-replay-test/test",
            region="us-east-1",
        )
        mock_create_table.assert_called()

    @patch("common.aws_service.glue_get_database", mock_glue_get_database)
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch(
        "common.aws_service.glue_get_table",
        Mock(side_effect=[TableNotFoundException("table"), mock_glue_get_table()]),
    )
    @patch("common.aws_service.glue_create_table")
    @patch(
        "common.aws_service.glue_get_partition_indexes",
        Mock(return_value={"PartitionIndexDescriptorList": None}),
    )
    def test_glue_cloning_table_not_found_in_table_copy_without_partitionIndex_descriptor_list(
        self, mock_create_table
    ):
        glue_util.clone_glue_catalog(
            records=[
                [
                    {"stringValue": "simple_replay"},
                    {"stringValue": "simple_replay_test_database"},
                    {"stringValue": "sales_data_table"},
                    {"stringValue": "simple_replay_cluster_datbase_9c8ff50e_a18f_11ed_8d98_02"},
                ]
            ],
            dest_location="s3://simple-replay-test/test",
            region="us-east-1",
        )
        mock_create_table.assert_called()


if __name__ == "__main__":
    unittest.main()
