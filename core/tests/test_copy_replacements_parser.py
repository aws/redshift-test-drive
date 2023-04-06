import unittest
from unittest.mock import patch, Mock, mock_open

from core.replay.copy_replacements_parser import parse_copy_replacements


class CopyReplacementsParserTests(unittest.TestCase):
    @patch("common.aws_service.s3_client_get_object")
    def test_parse_copy_replacements_s3(self, patched_get_object):
        workload_directory = "s3://test-bucket/test-folder/prefix"
        mock_body = Mock()
        mock_body.read.return_value = "HeaderA,HeaderB,HeaderC\nA,B,C".encode("utf-8")
        patched_get_object.return_value = {"Body": mock_body}
        result = parse_copy_replacements(workload_directory)

        self.assertEqual(result, {"A": ["B", "C"]})

    def test_parse_copy_replacements_local(self):
        with patch(
            "builtins.open", mock_open(read_data="HeaderA,HeaderB,HeaderC\nA,B,C")
        ) as patched_open:
            result = parse_copy_replacements("/tmp")

        self.assertEqual(result, {"A": ["B", "C"]})


if __name__ == "__main__":
    unittest.main()
