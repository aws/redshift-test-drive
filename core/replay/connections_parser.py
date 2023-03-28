import datetime
import json
import logging

import dateutil.parser
from boto3 import client

from common.util import matches_filters

logger = logging.getLogger("WorkloadReplicatorLogger")


def parse_connections(
    workload_directory,
    time_interval_between_transactions,
    time_interval_between_queries,
    filters,
):
    connections = []

    # total number of connections before filters are applied
    total_connections = 0

    if workload_directory.startswith("s3://"):
        workload_s3_location = workload_directory[5:].partition("/")
        bucket_name = workload_s3_location[0]
        prefix = workload_s3_location[2]
        s3_object = client("s3").get_object(
            Bucket=bucket_name, Key=prefix.rstrip("/") + "/connections.json"
        )
        connections_json = json.loads(s3_object["Body"].read())
    else:
        with open(
            workload_directory.rstrip("/") + "/connections.json", "r"
        ) as connections_file:
            connections_json = json.loads(connections_file.read())
            connections_file.close()

    for connection_json in connections_json:
        is_time_interval_between_transactions = {
            "": connection_json["time_interval_between_transactions"],
            "all on": True,
            "all off": False,
        }[time_interval_between_transactions]
        is_time_interval_between_queries = {
            "": connection_json["time_interval_between_queries"],
            "all on": "all on",
            "all off": "all off",
        }[time_interval_between_queries]

        try:
            if connection_json["session_initiation_time"]:
                session_initiation_time = dateutil.parser.isoparse(
                    connection_json["session_initiation_time"]
                ).replace(tzinfo=datetime.timezone.utc)
            else:
                session_initiation_time = None

            if connection_json["disconnection_time"]:
                disconnection_time = dateutil.parser.isoparse(
                    connection_json["disconnection_time"]
                ).replace(tzinfo=datetime.timezone.utc)
            else:
                disconnection_time = None
            connection_key = (
                f'{connection_json["database_name"]}_{connection_json["username"]}_'
                f'{connection_json["pid"]}'
            )
            connection = ConnectionLog(
                session_initiation_time,
                disconnection_time,
                connection_json["application_name"],
                connection_json["database_name"],
                connection_json["username"],
                connection_json["pid"],
                is_time_interval_between_transactions,
                is_time_interval_between_queries,
                connection_key,
            )
            if matches_filters(connection, filters):
                connections.append(connection)
            total_connections += 1
        except Exception as err:
            logger.error(f"Could not parse connection: \n{str(connection_json)}\n{err}")

    connections.sort(
        key=lambda conxn: conxn.session_initiation_time
        or datetime.datetime.utcfromtimestamp(0).replace(tzinfo=datetime.timezone.utc)
    )

    return connections, total_connections


class ConnectionLog:
    def __init__(
        self,
        session_initiation_time,
        disconnection_time,
        application_name,
        database_name,
        username,
        pid,
        time_interval_between_transactions,
        time_interval_between_queries,
        connection_key,
    ):
        self.session_initiation_time = session_initiation_time
        self.disconnection_time = disconnection_time
        self.application_name = application_name
        self.database_name = database_name
        self.username = username
        self.pid = pid
        self.query_index = 0
        self.time_interval_between_transactions = time_interval_between_transactions
        self.time_interval_between_queries = time_interval_between_queries
        self.connection_key = connection_key
        self.transactions = []

    def __str__(self):
        return (
            "Session initiation time: %s, Disconnection time: %s, Application name: %s, Database name: %s, "
            "Username; %s, PID: %s, Time interval between transactions: %s, Time interval between queries: %s, "
            "Number of transactions: %s"
            % (
                self.session_initiation_time.isoformat(),
                self.disconnection_time.isoformat(),
                self.application_name,
                self.database_name,
                self.username,
                self.pid,
                self.time_interval_between_transactions,
                self.time_interval_between_queries,
                len(self.transactions),
            )
        )

    def offset_ms(self, ref_time):
        return (self.session_initiation_time - ref_time).total_seconds() * 1000.0

    @staticmethod
    def supported_filters():
        return {"database_name", "username", "pid"}
