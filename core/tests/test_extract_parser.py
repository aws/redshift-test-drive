from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import Mock

from core.extract import extract_parser

from core.util.audit_logs_parsing import ConnectionLog

pid = "12324"
xid = "123142412"
start_time = datetime.fromisoformat("2023-01-01T00:00:00").replace(tzinfo=timezone.utc)
end_time = datetime.fromisoformat("2023-02-01T00:00:00").replace(tzinfo=timezone.utc)


class ExtractParserTestCases(TestCase):
    def test_parse_log_useractivitylog(self):
        mock_file = Mock()
        mock_file.readlines.return_value = [
            # valid log line
            f"'2023-01-01T00:00:00Z UTC [ db=testdb user=testuser pid={pid} userid=4 xid={xid} ]' LOG: SELECT * FROM TEST_TABLE LIMIT 10;".format(
                pid, xid
            ).encode(),
            # invalid log line
            f"'2023-01-01T01:00:00Z UTC [ db=testdb user=testuser pid={pid} userid=4 xid={xid} ]' LOG: call test.set($1, $2);".format(
                pid, xid
            ).encode(),
        ]
        logs = {}
        extract_parser.parse_log(
            mock_file, "useractivitylog", {}, {}, logs, set(), start_time, end_time
        )
        self.assertEqual(len(logs), 1)
        for key, value in logs.items():
            self.assertEqual(len(value), 1)
            log = value[0]
            self.assertEqual(log.xid, xid)
            self.assertEqual(log.pid, pid)
            self.assertEqual(log.text, "SELECT * FROM TEST_TABLE LIMIT 10;")

    def test_parse_log_connectionlog(self):
        mock_file = Mock()
        set_application_name_line = f"set application_name |Sun, 01 Jan 2023 01:05:07:124|[local] |{xid} |{pid}|testdb |testuser |test |12312|TLSv1.2 |TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 |0| | | |JDBC-1.2.54.1082 |Linux 5.4.0-1086-aws amd64 |Amazon Redshift JDBC Driver 1.2.54.1082 |none |0|02d54c77-8302-4ae6-8e83".format(
            xid, pid
        ).encode()
        mock_file.readlines.return_value = [
            f"initiating session |Sun, 01 Jan 2023 00:00:12:212|[local] | |{pid}|testdb |testuser |Ident |0| | |0| | | | | | | |0|03e74c8e-c3cb-4a98-a3d9".format(
                pid
            ).encode(),
            f"disconnecting session |Sun, 01 Jan 2023 00:02:21:471|[local] | |{pid}|testdb |testuser |Ident |7460885| | |0| | | | | | | |0|03e74c8e-c3cb-4a98-a3d9".format(
                pid
            ).encode(),
            set_application_name_line,
        ]
        connections = {}
        event_time = datetime.strptime(
            "Sun, 01 Jan 2023 01:05:07:124", "%a, %d %b %Y %H:%M:%S:%f"
        ).replace(tzinfo=timezone.utc)
        last_connection = ConnectionLog(event_time, end_time, "testdb", "testuser", pid)
        last_connections = {hash(set_application_name_line): last_connection.get_pk()}
        extract_parser.parse_log(
            mock_file,
            "connectionlog",
            connections,
            last_connections,
            {},
            set(),
            start_time,
            end_time,
        )
        print(list(connections.values())[0])
        print(last_connections)
