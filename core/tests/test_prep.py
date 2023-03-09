import unittest
from replay.prep import ReplayPrep


class TestFilters(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_filename(self):
        # test parsing a SQL filename
        filename = "mydb1-myuser-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "myuser")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_dash(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "my-user")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_email(self):
        # test parsing a SQL filename
        filename = "mydb1-user@sample.com-12345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertEqual(db_name, "mydb1")
        self.assertEqual(username, "user@sample.com")
        self.assertEqual(pid, "12345")
        self.assertEqual(xid, "531231")

    def test_parse_filename_with_dash_fail(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-12.345-531231.sql"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertTrue(all([_ is None for _ in (db_name, username, pid, xid)]))

    def test_parse_filename_incomplete(self):
        # test parsing a SQL filename
        filename = "mydb1-my-user-.txt"
        db_name, username, pid, xid = ReplayPrep.parse_filename(filename)
        self.assertTrue(all([_ is None for _ in (db_name, username, pid, xid)]))


if __name__ == "__main__":
    unittest.main()
