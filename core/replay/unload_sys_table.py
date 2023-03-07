from replay.prep import ReplayPrep
from common.util import db_connect
import re
import logging

logger = logging.getLogger("SimpleReplayLogger")


class UnloadSysTable:
    def __init__(self, config, replay_id):
        self.config = config
        self.default_interface = config["default_interface"]
        self.unload_system_table_queries_file = config["unload_system_table_queries"]
        self.unload_location = config["replay_output"] + "/" + replay_id
        self.unload_iam_role = config["target_cluster_system_table_unload_iam_role"]

    def unload_system_table(self):
        # TODO: wrap this in retries and proper logging
        prep = ReplayPrep(self.config)
        credentials = prep.get_connection_credentials(
            self.config["master_username"], max_attempts=3
        )
        conn = db_connect(
            self.default_interface,
            host=credentials["host"],
            port=int(credentials["port"]),
            username=credentials["username"],
            password=credentials["password"],
            database=credentials["database"],
            odbc_driver=credentials["odbc_driver"],
        )

        unload_queries = {}
        table_name = ""
        query_text = ""
        for line in open(self.unload_system_table_queries_file, "r"):
            if line.startswith("--"):
                unload_queries[table_name] = query_text.strip("\n")
                table_name = line[2:].strip("\n")
                query_text = ""
            else:
                query_text += line

        unload_queries[table_name] = query_text.strip("\n")
        del unload_queries[""]

        cursor = conn.cursor()
        for table_name, unload_query in unload_queries.items():
            if table_name and unload_query:
                unload_query = re.sub(
                    r"to ''",
                    f"TO '{self.unload_location}/system_tables/{table_name}/'",
                    unload_query,
                    flags=re.IGNORECASE,
                )
                unload_query = re.sub(
                    r"credentials ''",
                    f"CREDENTIALS 'aws_iam_role={self.unload_iam_role}'",
                    unload_query,
                    flags=re.IGNORECASE,
                )
                try:
                    cursor.execute(unload_query)
                except Exception as e:
                    logger.error(f"Failed to unload query. {e}")
                logger.debug(f"Executed unload query: {unload_query}")