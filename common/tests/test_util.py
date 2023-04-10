import unittest
from unittest import TestCase
from unittest.mock import patch, Mock

import redshift_connector

import common.util


class TestDbConnect(TestCase):
    @patch("redshift_connector.connect")
    def test_db_connect_psql_drop_return_true(self, mock_connect):
        mock_connection = Mock()
        mock_connection.message_types = {}
        mock_connect.return_value = mock_connection

        connection = common.util.db_connect(drop_return=True)
        self.assertEqual(connection, mock_connection)
        self.assertIsNotNone(connection.message_types[redshift_connector.core.DATA_ROW])

    @patch("redshift_connector.connect")
    def test_db_connect_psql_drop_return_false(self, mock_connect):
        mock_connection = Mock()
        mock_connection.message_types = {}
        mock_connect.return_value = mock_connection

        connection = common.util.db_connect()
        self.assertEqual(connection, mock_connection)
        self.assertIsNone(connection.message_types.get(redshift_connector.core.DATA_ROW, None))

    def test_db_connect_unsupported_interface(self):
        with self.assertRaises(ValueError) as _:
            common.util.db_connect("test")


class TestClusterDict(TestCase):
    @patch("common.aws_service.redshift_describe_clusters")
    def test_cluster_dict_provisioned_success(self, patched_redshift_describe_clusters):
        patched_redshift_describe_clusters.return_value = {
            "Clusters": [{"NumberOfNodes": "1", "NodeType": "ra3"}]
        }
        cluster = common.util.cluster_dict(
            endpoint="test.test.us-east-1.redshift.amazonaws.com:5439/dev",
            start_time="2021-08-15T15:50",
            end_time="2021-08-15T18:55",
        )
        self.assertEqual(cluster.get("num_nodes", None), "1")
        self.assertEqual(cluster.get("instance", None), "ra3")

    @patch("common.aws_service.redshift_describe_clusters")
    def test_cluster_dict_provisioned_success(self, patched_redshift_describe_clusters):
        patched_redshift_describe_clusters.side_effect = [Exception("Failed to describe clusters")]
        cluster = common.util.cluster_dict(
            endpoint="test.test.us-east-1.redshift.amazonaws.com:5439/dev",
            start_time="2021-08-15T15:50",
            end_time="2021-08-15T18:55",
        )
        self.assertEqual(cluster.get("num_nodes", None), "N/A")
        self.assertEqual(cluster.get("instance", None), "N/A")

    @patch("common.aws_service.redshift_get_serverless_workgroup")
    def test_cluster_dict_serverless_success(self, patched_get_serverless_workgroup):
        patched_get_serverless_workgroup.return_value = {"workgroup": {"baseCapacity": 10}}
        cluster = common.util.cluster_dict(
            endpoint="test.test.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
            start_time="2021-08-15T15:50",
            end_time="2021-08-15T18:55",
            is_serverless=True,
        )
        self.assertEqual(cluster.get("num_nodes", None), "N/A")
        self.assertEqual(cluster.get("instance", None), "Serverless")
        self.assertEqual(cluster.get("base_rpu", 0), 10)

    @patch("common.aws_service.redshift_get_serverless_workgroup")
    def test_cluster_dict_serverless_resource_not_found(self, patched_get_serverless_workgroup):
        e = Exception("Failed..")
        e.response = {"Error": {"Code": "ResourceNotFoundException"}}
        patched_get_serverless_workgroup.side_effect = [e]
        with self.assertRaises(Exception):
            common.util.cluster_dict(
                endpoint="test.test.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
                start_time="2021-08-15T15:50",
                end_time="2021-08-15T18:55",
                is_serverless=True,
            )

    @patch("common.aws_service.redshift_get_serverless_workgroup")
    def test_cluster_dict_serverless_internal_exception(self, patched_get_serverless_workgroup):
        e = Exception("Failed..")
        e.response = {"Error": {"Code": "InternalFailure"}}
        patched_get_serverless_workgroup.side_effect = [e]
        cluster = common.util.cluster_dict(
            endpoint="test.test.us-east-1.redshift-serverless.amazonaws.com:5439/dev",
            start_time="2021-08-15T15:50",
            end_time="2021-08-15T18:55",
            is_serverless=True,
        )
        self.assertEqual(cluster.get("num_nodes", None), "N/A")
        self.assertEqual(cluster.get("instance", None), "Serverless")
        self.assertEqual(cluster.get("base_rpu", 0), "N/A")


class TestBucketDict(unittest.TestCase):
    def test_bucket_dict(self):
        bucket_dict = common.util.bucket_dict("s3://test-bucket/test-key")
        self.assertEqual(bucket_dict.get("url", ""), "s3://test-bucket/test-key")
        self.assertEqual(bucket_dict.get("bucket_name", ""), "test-bucket")
        self.assertEqual(bucket_dict.get("prefix", ""), "test-key/")

    @patch("common.util.urlparse")
    def test_bucket_dict_urlparse_failure(self, patched_url_parse):
        patched_url_parse.side_effect = [ValueError("Failed")]
        with self.assertRaises(SystemExit):
            common.util.bucket_dict("s3://test-bucket/test-key")
