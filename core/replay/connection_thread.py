import copy
import datetime
import json
import logging
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from pathlib import Path

import sqlparse

from .prep import ReplayPrep
from common.util import (
    prepend_ids_to_logs,
    db_connect,
    current_offset_ms,
    remove_comments,
    parse_error,
)


class ConnectionThread(threading.Thread):
    logger = logging.getLogger("SimpleReplayWorkerLogger")

    def __init__(
        self,
        process_idx,
        job_id,
        connection_log,
        default_interface,
        odbc_driver,
        replay_start,
        first_event_time,
        error_logger,
        thread_stats,
        num_connections,
        peak_connections,
        connection_semaphore,
        perf_lock,
        config,
        total_connections,
    ):
        threading.Thread.__init__(self)
        self.process_idx = process_idx
        self.job_id = job_id
        self.connection_log = connection_log
        self.default_interface = default_interface
        self.odbc_driver = odbc_driver
        self.replay_start = replay_start
        self.first_event_time = first_event_time
        self.error_logger = error_logger
        self.thread_stats = thread_stats
        self.num_connections = num_connections
        self.peak_connections = peak_connections
        self.connection_semaphore = connection_semaphore
        self.perf_lock = perf_lock
        self.config = config
        self.total_connections = total_connections

        prepend_ids_to_logs(self.process_idx, self.job_id + 1)

    @contextmanager
    def initiate_connection(self, username):
        conn = None

        # check if this connection is happening at the right time
        expected_elapsed_sec = (
            self.connection_log.session_initiation_time - self.first_event_time
        ).total_seconds()
        elapsed_sec = (
            datetime.datetime.now(tz=datetime.timezone.utc) - self.replay_start
        ).total_seconds()
        connection_diff_sec = elapsed_sec - expected_elapsed_sec
        connection_duration_sec = (
            self.connection_log.disconnection_time
            - self.connection_log.session_initiation_time
        ).total_seconds()

        self.logger.debug(
            f"Establishing connection {self.job_id + 1} of {self.total_connections} at {elapsed_sec:.3f} "
            f"(expected: {expected_elapsed_sec:.3f}, {connection_diff_sec:+.3f}).  "
            f"Pid: {self.connection_log.pid}, Connection times: {self.connection_log.session_initiation_time} "
            f"to {self.connection_log.disconnection_time}, {connection_duration_sec} sec"
        )

        # save the connection difference
        self.thread_stats["connection_diff_sec"] = connection_diff_sec

        # and emit a warning if we're behind
        if abs(connection_diff_sec) > self.config.get("connection_tolerance_sec", 300):
            self.logger.warning(
                "Connection at {} offset by {:+.3f} sec".format(
                    self.connection_log.session_initiation_time, connection_diff_sec
                )
            )

        interface = self.default_interface

        if "psql" in self.connection_log.application_name.lower():
            interface = "psql"
        elif (
            "odbc" in self.connection_log.application_name.lower()
            and self.odbc_driver is not None
        ):
            interface = "odbc"
        elif self.default_interface == "odbc" and self.odbc_driver is None:
            self.logger.warning(
                "Default driver is set to ODBC. But no ODBC DSN provided. Replay will use PSQL as "
                "default driver."
            )
            interface = "psql"
        else:
            interface = "psql"
        r = ReplayPrep(self.config)
        credentials = r.get_connection_credentials(
            username, database=self.connection_log.database_name
        )

        try:
            try:
                conn = db_connect(
                    interface,
                    host=credentials["host"],
                    port=int(credentials["port"]),
                    username=credentials["username"],
                    password=credentials["password"],
                    database=credentials["database"],
                    odbc_driver=credentials["odbc_driver"],
                    drop_return=self.config.get("drop_return"),
                )
                self.logger.debug(
                    f"Connected using {interface} for PID: {self.connection_log.pid}"
                )
                self.num_connections.value += 1
            except Exception as err:
                hashed_cluster_url = copy.deepcopy(credentials)
                hashed_cluster_url["password"] = "***"
                self.logger.error(
                    f"({self.job_id + 1}) Failed to initiate connection for {self.connection_log.database_name}-"
                    f"{self.connection_log.username}-{self.connection_log.pid} ({hashed_cluster_url}): {err}"
                )
                self.thread_stats["connection_error_log"][
                    f"{self.connection_log.database_name}-{self.connection_log.username}-{self.connection_log.pid}"
                ] = f"{self.connection_log}\n\n{err}"
            yield conn
        except Exception as e:
            self.logger.error(f"Exception in connect: {e}")
        finally:
            self.logger.debug(f"Context closing for pid: {self.connection_log.pid}")
            if conn is not None:
                conn.close()
                self.logger.debug(f"Disconnected for PID: {self.connection_log.pid}")
            self.num_connections.value -= 1
            if self.connection_semaphore is not None:
                self.logger.debug(
                    f"Releasing semaphore ({self.num_connections.value} / "
                    f"{self.config['limit_concurrent_connections']} active connections)"
                )
                self.connection_semaphore.release()

    def run(self):
        try:
            with self.initiate_connection(self.connection_log.username) as connection:
                if connection:
                    self.execute_transactions(connection)
                    if self.connection_log.time_interval_between_transactions is True:
                        disconnect_offset_sec = (
                            self.connection_log.disconnection_time
                            - self.first_event_time
                        ).total_seconds()
                        if disconnect_offset_sec > current_offset_ms(self.replay_start):
                            self.logger.debug(
                                f"Waiting to disconnect {disconnect_offset_sec} sec (pid "
                                f"{self.connection_log.pid})"
                            )
                            time.sleep(disconnect_offset_sec)
                else:
                    self.logger.warning("Failed to connect")
        except Exception as e:
            self.logger.error(
                f"Exception thrown for pid {self.connection_log.pid}: {e}"
            )
            traceback.print_exc(file=sys.stderr)

    def execute_transactions(self, connection):
        if self.connection_log.time_interval_between_transactions is True:
            for idx, transaction in enumerate(self.connection_log.transactions):
                # we can use this if we want to run transactions based on their offset from the start of the replay
                # time_until_start_ms = transaction.offset_ms(self.first_event_time) -
                # current_offset_ms(self.replay_start)

                # or use this to preserve the time between transactions
                if idx == 0:
                    time_until_start_ms = (
                        transaction.start_time()
                        - self.connection_log.session_initiation_time
                    ).total_seconds() * 1000.0
                else:
                    prev_transaction = self.connection_log.transactions[idx - 1]
                    time_until_start_ms = (
                        transaction.start_time() - prev_transaction.end_time()
                    ).total_seconds() * 1000.0

                # wait for the transaction to start
                if time_until_start_ms > 10:
                    self.logger.warning(
                        f"Waiting {time_until_start_ms / 1000:.1f} sec for transaction to start"
                    )
                    time.sleep(time_until_start_ms / 1000.0)
                self.execute_transaction(transaction, connection)
        else:
            for transaction in self.connection_log.transactions:
                self.execute_transaction(transaction, connection)

    def save_query_stats(self, starttime, endtime, xid, query_idx):
        with self.perf_lock:
            sr_dir = (
                self.config.get("logging_dir", "simplereplay_logs")
                + "/"
                + self.replay_start.isoformat()
            )
            Path(sr_dir).mkdir(parents=True, exist_ok=True)
            filename = f"{sr_dir}/{self.process_idx}_times.csv"
            elapsed_sec = 0
            if endtime is not None:
                elapsed_sec = "{:.6f}".format((endtime - starttime).total_seconds())
            with open(filename, "a+") as fp:
                if fp.tell() == 0:
                    fp.write("# process,query,start_time,end_time,elapsed_sec,rows\n")
                query_id = f"{xid}-{query_idx}"
                fp.write(
                    "{},{},{},{},{},{}\n".format(
                        self.process_idx, query_id, starttime, endtime, elapsed_sec, 0
                    )
                )

    def get_tagged_sql(self, query_text, idx, transaction, connection):
        json_tags = {
            "xid": transaction.xid,
            "query_idx": idx,
            "replay_start": self.replay_start.isoformat(),
        }
        return "/* {} */ {}".format(json.dumps(json_tags), query_text)

    def execute_transaction(self, transaction, connection):
        errors = []
        cursor = connection.cursor()

        transaction_query_idx = 0
        for idx, query in enumerate(transaction.queries):
            time_until_start_ms = query.offset_ms(
                self.first_event_time
            ) - current_offset_ms(self.replay_start)
            truncated_query = (
                query.text[:60] + "..." if len(query.text) > 60 else query.text
            ).replace("\n", " ")
            self.logger.debug(
                f"Executing [{truncated_query}] in {time_until_start_ms / 1000.0:.1f} sec"
            )

            if time_until_start_ms > 10:
                time.sleep(time_until_start_ms / 1000.0)

            if self.config.get("split_multi", True):
                formatted_query = query.text.lower()
                if not formatted_query.startswith(("begin", "start")):
                    query_begin = "begin;" + formatted_query
                if not formatted_query.endswith(("commit", "end")):
                    query = query_begin + "commit;"
                split_statements = sqlparse.split(query)
                split_statements = [_ for _ in split_statements if _ != ";"]
            else:
                split_statements = [query.text]

            if len(split_statements) > 1:
                self.thread_stats["multi_statements"] += 1
            self.thread_stats["executed_queries"] += len(split_statements)

            success = True
            for s_idx, sql_text in enumerate(split_statements):
                sql_text = self.get_tagged_sql(
                    sql_text, transaction_query_idx, transaction, connection
                )
                transaction_query_idx += 1

                substatement_txt = ""
                if len(split_statements) > 1:
                    substatement_txt = (
                        f", Multistatement: {s_idx + 1}/{len(split_statements)}"
                    )

                exec_start = datetime.datetime.now(tz=datetime.timezone.utc)
                exec_end = None
                try:
                    status = ""
                    if (
                        self.config["execute_copy_statements"] == "true"
                        and "from 's3:" in sql_text.lower()
                    ):
                        cursor.execute(sql_text)
                    elif (
                        self.config["execute_unload_statements"] == "true"
                        and "to 's3:" in sql_text.lower()
                        and self.config["replay_output"] is not None
                    ):
                        cursor.execute(sql_text)
                    elif ("from 's3:" not in sql_text.lower()) and (
                        "to 's3:" not in sql_text.lower()
                    ):  ## removed condition to exclude bind variables
                        cursor.execute(sql_text)
                    else:
                        status = "Not "
                    exec_end = datetime.datetime.now(tz=datetime.timezone.utc)
                    exec_sec = (exec_end - exec_start).total_seconds()

                    self.logger.debug(
                        f"{status}Replayed DB={transaction.database_name}, USER={transaction.username}, PID={transaction.pid}, XID:{transaction.xid}, Query: {idx + 1}/{len(transaction.queries)}{substatement_txt} ({exec_sec} sec)"
                    )
                    success = success & True
                except Exception as err:
                    success = False
                    errors.append([sql_text, str(err)])
                    self.logger.debug(
                        f"Failed DB={transaction.database_name}, USER={transaction.username}, PID={transaction.pid}, "
                        f"XID:{transaction.xid}, Query: {idx + 1}/{len(transaction.queries)}{substatement_txt}: {err}"
                    )
                    self.error_logger.append(
                        parse_error(
                            err,
                            transaction.username,
                            self.config["target_cluster_endpoint"].split("/")[-1],
                            query.text,
                        )
                    )

                self.save_query_stats(
                    exec_start, exec_end, transaction.xid, transaction_query_idx
                )
            if success:
                self.thread_stats["query_success"] += 1
            else:
                self.thread_stats["query_error"] += 1

            if query.time_interval > 0.0:
                self.logger.debug(f"Waiting {query.time_interval} sec between queries")
                time.sleep(query.time_interval)

        cursor.close()
        connection.commit()

        if self.thread_stats["query_error"] == 0:
            self.thread_stats["transaction_success"] += 1
        else:
            self.thread_stats["transaction_error"] += 1
            self.thread_stats["transaction_error_log"][
                transaction.get_base_filename()
            ] = errors
