import unittest
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, mock_open
import dateutil
import yaml
import tools.ExternalObjectReplicator.external_object_replicator as eor

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
end_time = dateutil.parser.parse(config_file["end_time"]).astimezone(dateutil.tz.tzutc())
start_time = dateutil.parser.parse(config_file["start_time"]).astimezone(dateutil.tz.tzutc())

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
    @patch("tools.ExternalObjectReplicator.util.copy_util.clone_objects_to_s3")
    @patch("common.config.get_config_file_from_args", return_value=config_file)
    @patch("common.util.cluster_dict", return_value=cluster_obj)
    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.execute_svl_query",
        return_value=({"TotalNumRows": 1}, None, None, None),
    )
    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.execute_stl_load_query",
        return_value=({"TotalNumRows": 1}, None, None),
    )
    @patch("builtins.input", return_value=2)
    def test_main_not_proceed(
        self,
        mock_input,
        mock_execute_stl_load_query,
        mock_execute_svl_query,
        mock_cluster_dict,
        mock_get_config_file_from_args,
        mock_clone_objects_to_s3,
    ):
        eor.main()
        mock_execute_stl_load_query.assert_called_once_with(
            cluster_obj,
            end_time,
            config_file,
            "someuser",
            start_time,
        )
        mock_execute_svl_query.assert_called_once_with(
            cluster_obj,
            end_time,
            config_file,
            "someuser",
            start_time,
        )
        mock_clone_objects_to_s3.assert_not_called()

    @patch("common.config.get_config_file_from_args", return_value=config_file)
    @patch("tools.ExternalObjectReplicator.util.copy_util.clone_objects_to_s3", return_value=None)
    @patch("tools.ExternalObjectReplicator.util.glue_util.clone_glue_catalog", return_value=None)
    @patch("common.util.cluster_dict", return_value=cluster_obj)
    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.execute_svl_query",
        return_value=({"TotalNumRows": 1}, None, external_table_response, None),
    )
    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.execute_stl_load_query",
        return_value=({"TotalNumRows": 1}, None, None),
    )
    @patch("builtins.input", return_value=1)
    def test_main_proceed(
        self,
        mock_input,
        mock_execute_stl_load_query,
        mock_execute_svl_query,
        mock_cluster_dict,
        mock_clone_glue_catalog,
        mock_clone_objects_to_s3,
        mock_get_config_file_from_args,
    ):
        eor.main()
        mock_execute_stl_load_query.assert_called_once_with(
            cluster_obj,
            end_time,
            config_file,
            "someuser",
            start_time,
        )
        mock_execute_svl_query.assert_called_once_with(
            cluster_obj,
            end_time,
            config_file,
            "someuser",
            start_time,
        )
        mock_clone_objects_to_s3.assert_called()


class TestExecuteStlLoadQuery(IsolatedAsyncioTestCase):
    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.get_s3_folder_size",
        lambda copy_file_list: 10,
    )
    @patch("builtins.open", mock_open())
    @patch("tools.ExternalObjectReplicator.external_object_replicator.check_file_existence")
    @patch("tools.ExternalObjectReplicator.external_object_replicator.redshift_execute_query")
    def test_execute_stl_load_query_success(
        self, mock_redshift_execute_query, mock_check_file_existence
    ):
        expected_objects_found = ["A", "B", "C"]
        stubbed_query_response = {"TotalNumRows": 20, "Records": expected_objects_found}
        mock_redshift_execute_query.return_value = stubbed_query_response
        expected_objects_not_found = ["D"]
        mock_check_file_existence.return_value = expected_objects_found, expected_objects_not_found
        stl_load_response, objects_not_found, objects_found = eor.execute_stl_load_query(
            cluster_obj, end_time, config_file, "awsuser", start_time
        )
        self.assertEqual(stubbed_query_response, stl_load_response)
        self.assertEqual(objects_found, expected_objects_found)
        self.assertEqual(objects_not_found, expected_objects_not_found)

    @patch(
        "tools.ExternalObjectReplicator.external_object_replicator.get_s3_folder_size",
        lambda copy_file_list: 10,
    )
    @patch("builtins.open", mock_open())
    @patch("tools.ExternalObjectReplicator.external_object_replicator.check_file_existence")
    @patch("tools.ExternalObjectReplicator.external_object_replicator.redshift_execute_query")
    def test_execute_svl_load_query(self, mock_redshift_execute_query, mock_check_file_existence):
        stubbed_ext_table_query_response = {"TotalNumRows": 1}
        stubbed_svl_s3list_query_response = {"TotalNumRows": 2, "Records": []}
        mock_redshift_execute_query.side_effect = [
            stubbed_ext_table_query_response,
            stubbed_svl_s3list_query_response,
        ]
        expected_objects_found = ["A", "B", "C"]
        expected_objects_not_found = ["D"]

        mock_check_file_existence.return_value = expected_objects_found, expected_objects_not_found

        (
            svl_s3list_result,
            objects_found,
            external_table_response,
            objects_not_found,
        ) = eor.execute_svl_query(cluster_obj, end_time, config_file, "awsuser", start_time)
        self.assertEqual(svl_s3list_result, stubbed_svl_s3list_query_response)
        self.assertEqual(objects_found, expected_objects_found)
        self.assertEqual(external_table_response, stubbed_ext_table_query_response)
        self.assertEqual(objects_not_found, expected_objects_not_found)


if __name__ == "__main__":
    unittest.main()
