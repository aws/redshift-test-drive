import unittest
from unittest.mock import patch, Mock

from extract.local_extractor import LocalExtractor


class LocalExtractorTestCases(unittest.TestCase):
    def test_extract_locally(self):
        with patch("os.listdir") as mock_list_dir:
            with patch("gzip.open") as mock_gzip_open:
                with patch("extract.extract_parser.parse_log") as mock_parse_log:
                    mock_list_dir.return_value = [
                        "start_node.log.gz",
                        "useractivity.log.gz",
                        "connections.log.gz",
                    ]
                    mock_gzip_open.return_value = Mock()
                    mock_parse_log.return_value = None
                    e = LocalExtractor({})
                    e.get_extract_locally(
                        "test", "2022-11-16T00:00:00", "2022-11-18T00:00:00"
                    )
        self.assertTrue(mock_list_dir.called)
        self.assertTrue(mock_gzip_open.called)
        self.assertTrue(mock_parse_log.called)


if __name__ == "__main__":
    unittest.main()
