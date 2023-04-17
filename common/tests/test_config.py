import datetime
import os
import unittest
from argparse import ArgumentParser
from unittest.mock import patch, Mock
import io
import common.config as config_helper
import yaml
import copy

curr_dir = os.path.dirname(os.path.realpath(__file__))
with open(curr_dir + "/testdata/config.yaml") as stream:
    config = yaml.safe_load(stream)
    config_original = config

with open(curr_dir + "/testdata/config_ext.yaml") as stream:
    config_ext = yaml.safe_load(stream)
    config_ext_original = config_ext

config_yaml = """
         "source_cluster_endpoint": "someendpoint"
         "region": "us-east-1"
         "redshift_user": "someuser"
         "start_time": "2023-01-31 6:00:29"
         "end_time": "2023-01-31 10:11:57"
         "target_s3_location": "somelocation"
         "log_level": Debug
       """


def get_parsed_args(_):
    mock_parse_args = Mock()
    reader = io.BufferedReader(io.BytesIO(config_yaml.encode("utf-8")))
    wrapper = io.TextIOWrapper(reader)
    mock_parse_args.__setattr__("config_file", wrapper)
    return mock_parse_args


class TestGetConfigFileFromArgs(unittest.TestCase):
    # need to write test case for argparse
    @patch.object(ArgumentParser, "parse_args", get_parsed_args)
    def test_get_config_file_from_args(self):
        config_file = config_helper.get_config_file_from_args()
        self.assertEqual(config_file.get("source_cluster_endpoint"), "someendpoint")
        self.assertEqual(config_file.get("region"), "us-east-1")
        self.assertEqual(config_file.get("redshift_user"), "someuser")

    @patch("yaml.safe_load", Mock(side_effect=[yaml.YAMLError]))
    @patch.object(ArgumentParser, "parse_args", get_parsed_args)
    def test_get_config_file_from_args_with_yaml_error(self):
        with self.assertRaises(SystemExit):
            config_helper.get_config_file_from_args()


# extract yaml test
class TestValidateConfigForExtract(unittest.TestCase):
    def setUp(self):
        self.config = copy.deepcopy(config_original)
        self.config_ext = copy.deepcopy(config_ext_original)

    def test_validate_config_file_for_extract_source_cluster_endpoint_serverless(self):
        self.config_ext[
            "source_cluster_endpoint"
        ] = "test.111222333222.us-east-1redshift-serverless.amazonaws.com:5439/dev"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_source_cluster_endpoint(self):
        self.config_ext[
            "source_cluster_endpoint"
        ] = "sr-test.cqm7brtjbnqz.us-east-1redshift.amazonaws.com:5439/dev"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_master_username(self):
        self.config_ext["master_username"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_region(self):
        self.config_ext["region"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_log_location(self):
        self.config_ext["source_cluster_endpoint"] = ""
        self.config_ext["log_location"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_start_time(self):
        self.config_ext["start_time"] = "2022-12-2716:40:1"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_external_schemas(self):
        self.config_ext["external_schemas"] = "test_schema"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_end_time(self):
        self.config_ext["end_time"] = "2022-12-2716:40:1"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_workload_location(self):
        self.config_ext["workload_location"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_source_cluster_system_table_unload(self):
        self.config_ext["source_cluster_system_table_unload_location"] = "test-location"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_no_iam_role(self):
        self.config_ext["source_cluster_system_table_unload_location"] = "s3://test-location"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_no_unload_queries(self):
        self.config_ext["source_cluster_system_table_unload_location"] = "s3://test-location"
        self.config_ext["source_cluster_system_table_unload_iam_role"] = "arn::iam:role/dev"
        self.config_ext["unload_system_table_queries"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_for_extract_unload_query_file_format(self):
        self.config_ext["source_cluster_system_table_unload_location"] = "s3://test-location"
        self.config_ext["source_cluster_system_table_unload_iam_role"] = "arn::iam:role/dev"
        self.config_ext["unload_system_table_queries"] = "unload_system_tables.py"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_file_for_extract(self.config_ext)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_file_no_source_cluster_endpoint_or_log_location(self):
        self.config_ext["source_cluster_endpoint"] = None
        self.config_ext["log_location"] = None
        with self.assertRaises(SystemExit):
            config_helper.validate_config_file_for_extract(self.config_ext)

    def test_validate_config_file_with_start_time(self):
        self.config_ext["region"] = "us-east-1"
        self.config_ext["start_time"] = "2023-01-10T14:59:27+00:00"
        self.config_ext["workload_location"] = "s3://test-bucket/workload_location"
        config_helper.validate_config_file_for_extract(self.config_ext)
        self.config_ext["start_time"] = "2023-01-10T15:00m"
        with self.assertRaises(SystemExit):
            config_helper.validate_config_file_for_extract(self.config_ext)

    def test_validate_config_file_with_external_schemas(self):
        self.config_ext["region"] = "us-east-1"
        self.config_ext["start_time"] = "2023-01-10T14:59:27+00:00"
        self.config_ext["workload_location"] = "s3://test-bucket/workload_location"
        self.config_ext["external_schemas"] = ["test"]
        config_helper.validate_config_file_for_extract(self.config_ext)
        self.config_ext["external_schemas"] = "test"
        with self.assertRaises(SystemExit):
            config_helper.validate_config_file_for_extract(self.config_ext)

    def test_validate_config_file_with_end_time(self):
        self.config_ext["region"] = "us-east-1"
        self.config_ext["end_time"] = "2023-01-10T14:59:27+00:00"
        self.config_ext["workload_location"] = "s3://test-bucket/workload_location"
        config_helper.validate_config_file_for_extract(self.config_ext)
        self.config_ext["end_time"] = "2023-01-10T15:00m"
        with self.assertRaises(SystemExit):
            config_helper.validate_config_file_for_extract(self.config_ext)


# Replay yaml test
class TestValidateConfigForReplay(unittest.TestCase):
    def setUp(self):
        self.config = copy.deepcopy(config_original)
        self.config_ext = copy.deepcopy(config_ext_original)

    def test_validate_config_for_replay_target_cluster_endpoint(self):
        self.config[
            "target_cluster_endpoint"
        ] = "test.111222333222us-east-1.redshift-serverless.amazonaws.com:5439/dev"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_no_target_cluster_endpoint(self):
        self.config["target_cluster_region"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_no_odbc(self):
        self.config["odbc_driver"] = ""
        config_helper.validate_config_for_replay(self.config)
        self.assertEqual(self.config["odbc_driver"], None)

    def test_validate_config_for_replay_odbc(self):
        self.config["odbc_driver"] = "odbc"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_wrong_interface(self):
        self.config["default_interface"] = "JDBC"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_time_transactions(self):
        self.config["time_interval_between_transactions"] = "all false"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_time_queries(self):
        self.config["time_interval_between_queries"] = "all false"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_copy(self):
        self.config["execute_copy_statements"] = "not true"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_unload(self):
        self.config["execute_unload_statements"] = "not true"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_replay_output(self):
        self.config["replay_output"] = "test-location"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_replay_output_format(self):
        self.config["replay_output"] = ""
        self.config["execute_unload_statements"] = "true"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_unload_table(self):
        self.config["replay_output"] = "s3://test-location"
        self.config["target_cluster_system_table_unload_iam_role"] = "arn::iam:role/dev"
        self.config["unload_system_table_queries"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_unload_table_format(self):
        self.config["replay_output"] = "s3://test-location"
        self.config["target_cluster_system_table_unload_iam_role"] = "arn::iam:role/dev"
        self.config["unload_system_table_queries"] = "unload_system_tables.py"
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_workload_location(self):
        self.config["workload_location"] = ""
        with self.assertRaises(SystemExit) as cm:
            config_helper.validate_config_for_replay(self.config)
        self.assertEqual(cm.exception.code, -1)

    def test_validate_config_for_replay_nlb_nat(self):
        config_helper.validate_config_for_replay(self.config)
        self.assertEqual(self.config["nlb_nat_dns"], None)

        self.assertEqual(self.config["secret_name"], None)
