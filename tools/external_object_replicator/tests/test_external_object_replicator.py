import os
import sys
import unittest
from unittest.mock import patch
import dateutil
import yaml
import
import external_object_replicator_util.copy_util
import external_object_replicator as eor
import external_object_replicator_util.glue_util
import external_object_replicator_util.query_executor


return_val = ({"TotalNumRows": 1}, None, None, None)

config_yaml = """
         "source_cluster_endpoint": someendpoint"
         "region": "us-east-1"
         "redshift_user": "someuser"
         "start_time": "2023-01-31 6:00:29"
         "end_time": "2023-01-31 10:11:57"
         "target_s3_location": "somelocation"
         "log_level": Debug
       """
config_file = yaml.safe_load(config_yaml)

cluster_obj = {
    "endpoint": "someendpoint",
    "id": "someid",
    "host": "somehost",
    "region": "us-east-1",
    "port": "5439",
    "database": "somedb",
    "is_serverless": False,
    "num_nodes": 2,
    "instance": "ra3.4xlarge",
}

external_table_response = {"Records": ""}

class MainTest(unittest.TestCase):

    @patch("helper.config.get_config_file_from_args", return_value=config_file)
    @patch("util.cluster_dict", return_value=cluster_obj)
    @patch("external_object_replicator_util.query_executor.execute_svl_query", return_value=({"TotalNumRows": 1}, None, None, None))
    @patch("external_object_replicator_util.query_executor.execute_stl_load_query",
           return_value=({"TotalNumRows": 1}, None, None))
    @patch('builtins.input', return_value=2)
    def test_main_not_proceed(self, mock_input, mock_execute_stl_load_query, mock_execute_svl_query, mock_cluster_dict,
                           mock_get_config_file_from_args):
        with self.assertRaises(SystemExit) as context:
            eor.main()
        mock_execute_stl_load_query.assert_called_once_with(cluster_obj,
                                                            dateutil.parser.parse(
                                                                config_file["end_time"]).astimezone(
                                                                dateutil.tz.tzutc()),
                                                            config_file, "someuser",
                                                            dateutil.parser.parse(
                                                                config_file["start_time"]).astimezone(
                                                                dateutil.tz.tzutc()))
        mock_execute_svl_query.assert_called_once_with(cluster_obj,
                                                       dateutil.parser.parse(config_file["end_time"]).astimezone(
                                                           dateutil.tz.tzutc()),
                                                       config_file, "someuser",
                                                       dateutil.parser.parse(config_file["start_time"]).astimezone(
                                                           dateutil.tz.tzutc()))

    @patch("helper.config.get_config_file_from_args", return_value=config_file)
    @patch("external_object_replicator_util.copy_util.clone_objects_to_s3", return_value=None)
    @patch("external_object_replicator_util.glue_util.clone_glue_catalog", return_value=None)
    @patch("util.cluster_dict", return_value=cluster_obj)
    @patch("external_object_replicator_util.query_executor.execute_svl_query", return_value=({"TotalNumRows": 1}, None, external_table_response, None))
    @patch("external_object_replicator_util.query_executor.execute_stl_load_query",
           return_value=({"TotalNumRows": 1}, None, None))
    @patch('builtins.input', return_value=1)
    def test_main_proceed(self, mock_input, mock_execute_stl_load_query, mock_execute_svl_query, mock_cluster_dict,
                          mock_clone_glue_catalog, mock_clone_objects_to_s3,  mock_get_config_file_from_args):
        eor.main()
        mock_execute_stl_load_query.assert_called_once_with(cluster_obj,
                                                            dateutil.parser.parse(
                                                                config_file["end_time"]).astimezone(
                                                                dateutil.tz.tzutc()),
                                                            config_file, "someuser",
                                                            dateutil.parser.parse(
                                                                config_file["start_time"]).astimezone(
                                                                dateutil.tz.tzutc()))
        mock_execute_svl_query.assert_called_once_with(cluster_obj,
                                                       dateutil.parser.parse(config_file["end_time"]).astimezone(
                                                           dateutil.tz.tzutc()),
                                                       config_file, "someuser",
                                                       dateutil.parser.parse(config_file["start_time"]).astimezone(
                                                           dateutil.tz.tzutc()))


if __name__ == "__main__":
    unittest.main()