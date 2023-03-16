import unittest
from unittest.mock import patch
import sys

sys.path.append("../")
from tools.ExternalObjectReplicator.util import glue_util


def mock_glue_get_database(name, region):
    return {}


def mock_create_database(name, message, region):
    return {}


def mock_glue_get_table(database, table, region):
    return {"Table": {"StorageDescriptor": {"Location": "s3://Test"}}}


def mock_glue_get_partition_indexes(database, table, region):
    return {"PartitionIndexDescriptorList"}


def mock_glue_create_table(database, table_input, region):
    return {}


class GlueUtilTestCases(unittest.TestCase):
    @patch("common.aws_service.glue_get_database", mock_glue_get_database)
    @patch("common.aws_service.glue_create_database", mock_create_database)
    @patch("common.aws_service.glue_get_table", mock_glue_get_table)
    @patch("common.aws_service.glue_create_table", mock_glue_create_table)
    @patch(
        "common.aws_service.glue_get_partition_indexes", mock_glue_get_partition_indexes
    )
    def test_glue_cloning(self):
        response = glue_util.clone_glue_catalog(
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
        self.assertTrue(response)


if __name__ == "__main__":
    unittest.main()
