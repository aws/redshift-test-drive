import base64
import datetime
from unittest import TestCase, mock, IsolatedAsyncioTestCase
from unittest.mock import patch, Mock, MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError

import common.aws_service as aws_service_helper
from botocore.stub import Stubber

redshift_client = boto3.client("redshift", "us-east-1")
cw_client = boto3.client("logs", "us-east-1")
s3_client = boto3.client("s3", "us-east-1")
s3_resource = boto3.resource("s3", "us-east-1")
redshift_serverless_client = boto3.client("redshift-serverless", "us-east-1")
redshift_data_client = boto3.client("redshift-data", "us-east-1")
secretsmanager_client = boto3.client("secretsmanager", "us-east-1")
mock_redshift_client = mock.MagicMock(return_value=redshift_client)
mock_redshift_serverless_client = mock.MagicMock(return_value=redshift_serverless_client)
mock_redshift_data_client = mock.MagicMock(return_value=redshift_data_client)
mock_cw_client = mock.MagicMock(return_value=cw_client)
mock_s3_client = mock.MagicMock(return_value=s3_client)
mock_s3_resource = mock.MagicMock(return_value=s3_resource)
mock_secretsmanager_client = mock.MagicMock(return_value=secretsmanager_client)


class RedshiftTestCases(TestCase):
    @patch("boto3.client", mock_redshift_serverless_client)
    def test_redshift_get_serverless_workgroup(self):
        s = Stubber(redshift_serverless_client)
        expected_response = {"workgroup": {}}
        s.add_response("get_workgroup", expected_response)
        s.activate()
        actual_response = aws_service_helper.redshift_get_serverless_workgroup(
            "workgroup_name", "us-east-1"
        )
        self.assertEqual(actual_response, expected_response)
        s.deactivate()

    @patch("boto3.client", mock_redshift_client)
    def test_redshift_describe_clusters(self):
        s = Stubber(redshift_client)
        s.add_response("describe_clusters", {})
        s.activate()
        response = aws_service_helper.redshift_describe_clusters("cluster_id", "us-east-1")
        self.assertEqual(response, {})
        s.deactivate()

    @patch("boto3.client", mock_redshift_client)
    def test_redshift_describe_logging_status(self):
        s = Stubber(redshift_client)
        s.add_response("describe_logging_status", {})
        s.activate()
        response = aws_service_helper.redshift_describe_logging_status("test.t.us-east-1")
        assert response == {}
        s.deactivate()

    @patch("boto3.client", mock_redshift_client)
    def test_redshift_get_cluster_credentials_success(self):
        s = Stubber(redshift_client)
        s.add_response("get_cluster_credentials", {})
        s.activate()
        response = aws_service_helper.redshift_get_cluster_credentials(
            "us-east-1", "awsuser", "test", "testing"
        )
        self.assertEqual(response, {})
        s.deactivate()

    @patch("boto3.client", mock_redshift_client)
    def test_redshift_get_cluster_credentials_failure(self):
        s = Stubber(redshift_client)
        s.add_client_error(
            "get_cluster_credentials",
            service_error_code=redshift_client.exceptions.ClusterNotFoundFault,
        )
        s.activate()
        with self.assertRaises(SystemExit):
            aws_service_helper.redshift_get_cluster_credentials(
                "us-east-1", "awsuser", "test", "testing"
            )
        s.deactivate()

    @patch("boto3.client", mock_redshift_data_client)
    def test_redshift_execute_query_success(self):
        s = Stubber(redshift_data_client)
        s.add_response("execute_statement", {"Id": "abc"})
        s.add_response(
            "describe_statement", {"Id": "abc", "Status": "FINISHED", "HasResultSet": True}
        )
        s.add_response("get_statement_result", {"Records": []})

        s.activate()
        result = aws_service_helper.redshift_execute_query(
            "cluster_id", "awsuser", "testing", "us-east-1", "select * from id;"
        )
        self.assertEqual(result, {"Records": []})
        s.deactivate()

    @patch("boto3.client", mock_redshift_data_client)
    def test_redshift_execute_query_failure(self):
        s = Stubber(redshift_data_client)
        s.add_response("execute_statement", {"Id": "abc"})
        s.add_response("describe_statement", {"Id": "abc", "Status": "FAILED"})

        s.activate()
        with self.assertRaises(Exception):
            aws_service_helper.redshift_execute_query(
                "cluster_id", "awsuser", "testing", "us-east-1", "select * from id;"
            )

        s.deactivate()


class CloudwatchTestCases(TestCase):
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
        s.add_response("filter_log_events", {"nextToken": "abc", "events": [{"message": "ABC"}]})
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


class S3TestCases(TestCase):
    @patch("boto3.resource")
    def test_s3_upload(self, patched_boto3_resource):
        mock_object = {}
        mock_meta = MagicMock()
        mock_client = MagicMock()
        mock_client.upload_file.return_value = None
        mock_meta.client.return_value = mock_client
        mock_s3_resource.Object.return_value = mock_object
        mock_s3_resource.meta.return_value = mock_meta
        patched_boto3_resource.return_value = mock_s3_resource

        self.assertDictEqual(aws_service_helper.s3_upload("Test", "TestBucket", "TestKey"), {})

    @patch("boto3.client", mock_s3_client)
    def test_s3_client_put_object(self):
        s = Stubber(s3_client)
        s.add_response("put_object", {})
        s.activate()
        self.assertIsNone(aws_service_helper.s3_put_object("test", "bucket", "key"))
        s.deactivate()

    @patch("boto3.client", mock_s3_client)
    def test_s3_client_get_object(self):
        s = Stubber(s3_client)
        s.add_response("get_object", {})
        s.activate()
        aws_call = aws_service_helper.s3_client_get_object("bucket", "key")
        assert aws_call == {}
        s.deactivate()

    @patch("boto3.resource")
    def test_s3_resource_put_object(self, mock_s3_resource):
        mock_object = MagicMock()
        mock_put = MagicMock()
        mock_s3_resource.return_value.Object = mock_object
        mock_object.return_value.put = mock_put
        aws_service_helper.s3_resource_put_object("bucket", "key", "body")
        mock_object.assert_called_with("bucket", "key")
        mock_put.assert_called_once_with(Body="body")

    @patch("boto3.client", mock_s3_client)
    def test_generate_presigned_url(self):
        mock_generate_url = Mock()
        mock_s3_client.return_value.generate_presigned_url = mock_generate_url
        mock_generate_url.return_value = {}
        aws_call = aws_service_helper.s3_generate_presigned_url("clientmethod", "bucket", "key")
        assert aws_call == {}


class AsyncS3TestCase(IsolatedAsyncioTestCase):
    @patch("boto3.client", mock_s3_client)
    async def test_s3_get_bucket_contents(self):
        s = Stubber(s3_client)
        response_with_continuation_token = {
            "Contents": [{"Key": "Object1"}],
            "NextContinuationToken": "ABC",
            "IsTruncated": True,
        }
        response_without_continuation_token = {
            "Contents": [{"Key": "Object2"}],
            "IsTruncated": False,
        }
        s.add_response("list_objects_v2", response_with_continuation_token)
        s.add_response("list_objects_v2", response_without_continuation_token)
        s.activate()
        objects = await aws_service_helper.s3_get_bucket_contents("bucket", "prefix")
        self.assertEqual(objects, [{"Key": "Object1"}, {"Key": "Object2"}])
        s.deactivate()


class SecretsManagerTestCase(TestCase):
    @patch("boto3.client", mock_secretsmanager_client)
    def test_get_secret_string_success(self):
        s = Stubber(secretsmanager_client)
        s.add_response(
            "get_secret_value",
            {"SecretString": '{\n  "username":"TestUsername",\n  "password":"TestPwd"\n}\n'},
        )
        s.activate()
        secret = aws_service_helper.get_secret("secret_name", "us-east-1")
        s.deactivate()
        self.assertEqual(secret, {"username": "TestUsername", "password": "TestPwd"})

    @patch("boto3.client", mock_secretsmanager_client)
    def test_get_secret_binary_success(self):
        s = Stubber(secretsmanager_client)
        s.add_response(
            "get_secret_value",
            {
                "SecretBinary": base64.b64encode(
                    bytes('{\n  "username":"TestUsername",\n  "password":"TestPwd"\n}\n', "utf-8")
                )
            },
        )
        s.activate()
        secret = aws_service_helper.get_secret("secret_name", "us-east-1")
        s.deactivate()
        self.assertEqual(secret, {"username": "TestUsername", "password": "TestPwd"})

    @patch("boto3.client", mock_secretsmanager_client)
    def test_get_secret_client_error(self):
        s = Stubber(secretsmanager_client)
        s.add_client_error("get_secret_value", service_error_code="DecryptionFailureException")
        s.activate()
        with self.assertRaises(ClientError):
            aws_service_helper.get_secret("secret_name", "us-east-1")
        s.deactivate()
