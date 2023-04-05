import unittest
import common.config as config_helper
import yaml
import copy

with open("core/tests/testdata/config.yaml") as stream:
    config = yaml.safe_load(stream)
    config_original = config

with open("core/tests/testdata/config_ext.yaml") as stream:
    config_ext = yaml.safe_load(stream)
    config_ext_original = config_ext


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = copy.deepcopy(config_original)
        self.config_ext = copy.deepcopy(config_ext_original)

    # need to write test case for argparse
    def test_get_config_file_from_args(self):
        pass

    # extract yaml test
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

    # Replay yaml test
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
