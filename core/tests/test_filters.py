import unittest
from core.replay.connections_parser import ConnectionLog
from core.replay.prep import ReplayPrep
from common.util import matches_filters
import datetime
import yaml


class TestFilters(unittest.TestCase):
    def setUp(self):
        self._connection = ConnectionLog(
            datetime.datetime.now(),
            datetime.datetime.now(),
            "db1",
            "user1",
            123,
            "app",
            True,
            True,
            "key",
        )

    def test_matches_include_wildcard(self):
        filter_str = """filters:
                          include:
                              username: ['*']
                          exclude:
                              database_name: ['']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

    def test_matches_include_wildcard_with_exclude(self):
        filter_str = """filters:
                          include:
                              username: ['*']
                          exclude:
                              username: ['different_user1', 'different_user2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

    def test_matches_include_with_exclude1(self):
        filter_str = """filters:
                          include:
                              username: ['user1', 'user2']
                          exclude:
                              username: ['different_user1', 'different_user2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

    def test_matches_include_with_exclude2(self):
        filter_str = """filters:
                          include:
                              username: ['user1']
                          exclude:
                              username: ['different_user1', 'different_user2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

    def test_matches_include_with_exclude_wildcard(self):
        filter_str = """filters:
                          include:
                              database_name: ['db1']
                          exclude:
                              database_name: ['*']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user1', 'user2']
                          exclude:
                              username: ['*']
                     """
        config = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

    def test_notmatches_include_wildcard_with_exclude(self):
        filter_str = """filters:
                          include:
                              database_name: ['*']
                          exclude:
                              database_name: ['db1']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['*']
                          exclude:
                              username: ['db1', 'db2']
                     """
        config = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

    def test_notmatches_include_with_exclude(self):
        filter_str = """filters:
                          include:
                              database_name: ['db2', 'db3']
                          exclude:
                              database_name: ['db1']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user3', 'user4']
                          exclude:
                              username: ['user1', 'user2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

    def test_multiple_conditions_notmatch(self):
        filter_str = """filters:
                          include:
                              database_name: ['db1', 'db2']
                              username: ['different_user']
                          exclude:
                              database_name: ['db3']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user3', 'user4']
                          exclude:
                              database_name: ['db1']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user1', 'user2']
                          exclude:
                              database_name: ['db1']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user2', 'user3']
                          exclude:
                              database_name: ['db2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user1', 'user2']
                              pid: ['123', '124', '125']
                          exclude:
                              database_name: ['db2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertFalse(matches_filters(self._connection, filters))

    def test_multiple_conditions_match(self):
        filter_str = """filters:
                          include:
                              username: ['user1']
                              database_name: ['db1', 'db2']
                          exclude:
                              database_name: ['db3']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))

        filter_str = """filters:
                          include:
                              username: ['user1', 'user2']
                              pid: [123, 124, 125]
                          exclude:
                              database_name: ['db2']
                     """
        filters = ReplayPrep.validate_and_normalize_filters(
            ConnectionLog, yaml.safe_load(filter_str)["filters"]
        )
        self.assertTrue(matches_filters(self._connection, filters))


if __name__ == "__main__":
    unittest.main()
