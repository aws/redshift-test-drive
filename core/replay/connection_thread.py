import copy
import datetime
import json
import logging
import re
import threading
import time
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

import sqlparse

from core.replay.prep import ReplayPrep
from common.util import (
    db_connect,
    current_offset_ms,
)


class ConnectionThread(threading.Thread):
    logger = logging.getLogger("WorkloadReplicatorWorkerLogger")

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
            self.connection_log.disconnection_time - self.connection_log.session_initiation_time
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

        if self.connection_log.application_name == "psql":
            interface = "psql"
        elif self.connection_log.application_name == "odbc" and self.odbc_driver is not None:
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
        ##Fix IAM user bug. G.Bai - mar 2025
        if username[:4] == "IAM:" or username[:5] == "IAMR:" or username.count(":") == 2:
            self.logger.debug("Replace user - " + username + " to " + self.config["master_username"])
            username = self.config["master_username"]
        credentials = r.get_connection_credentials(username, database=self.connection_log.database_name)

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
                    f"{self.connection_log.username}-{self.connection_log.pid} ({hashed_cluster_url}): {err}",
                    exc_info=True,
                )
                self.thread_stats["connection_error_log"][
                    f"{self.connection_log.database_name}-{self.connection_log.username}-{self.connection_log.pid}"
                ] = f"{self.connection_log}\n\n{err}"
            yield conn
        except Exception as e:
            self.logger.error(f"Exception in connect: {e}", exc_info=True)
            self.logger.debug("".join(traceback.format_exception(*sys.exc_info())))

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
                            self.connection_log.disconnection_time - self.first_event_time
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
                f"Exception thrown for pid {self.connection_log.pid}: {e}",
                exc_info=True,
            )
            sys.exit(-1)

    def execute_transactions(self, connection):
        if self.connection_log.time_interval_between_transactions is True:
            for idx, transaction in enumerate(self.connection_log.transactions):
                # we can use this if we want to run transactions based on their offset from the start of the replay
                # time_until_start_ms = transaction.offset_ms(self.first_event_time) -
                # current_offset_ms(self.replay_start)

                # or use this to preserve the time between transactions
                if idx == 0:
                    time_until_start_ms = (
                        transaction.start_time() - self.connection_log.session_initiation_time
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

    def execute_transaction(self, transaction, connection):
        errors = []
        cursor = connection.cursor()

        transaction_query_idx = 0
        for idx, query in enumerate(transaction.queries):
            time_until_start_ms = query.offset_ms(self.first_event_time) - current_offset_ms(
                self.replay_start
            )
            truncated_query = (
                query.text[:60] + "..." if len(query.text) > 60 else query.text
            ).replace("\n", " ")
            self.logger.debug(
                f"Executing [{truncated_query}] in {time_until_start_ms / 1000.0:.1f} sec"
            )
            if time_until_start_ms > 10:
                time.sleep(time_until_start_ms / 1000.0)
            if self.config.get("split_multi", True) and query.text is not None:
                formatted_query = query.text.lower()
                if not formatted_query.startswith(("begin", "start")):
                    formatted_query = "begin;" + formatted_query
                if not formatted_query.endswith(("commit", "end")):
                    if not formatted_query.endswith(";"):
                        formatted_query = formatted_query + ";"
                    formatted_query = formatted_query + "commit;"
                split_statements = sqlparse.split(query.text)
                split_statements = [
                    statement for statement in split_statements if statement != ";"
                ]
                self.thread_stats["multi_statements"] += 1
            else:
                split_statements = [query.text]

            if len(split_statements) > 1:
                self.thread_stats["multi_statements"] += 1
            self.thread_stats["executed_queries"] += len(split_statements)

            success = True
            for s_idx, sql_text in enumerate(split_statements):
                json_tags = {
                    "xid": transaction.xid,
                    "query_idx": idx,
                    "replay_start": self.replay_start.isoformat(),
                    "source": "Test-Drive",
                }
                sql_text = "/* {} */ {}".format(json.dumps(json_tags), sql_text)
                transaction_query_idx += 1

                substatement_txt = ""
                if len(split_statements) > 1:
                    substatement_txt = f", Multistatement: {s_idx + 1}/{len(split_statements)}"

                exec_start = datetime.datetime.now(tz=datetime.timezone.utc)
                exec_end = None
                try:
                    status = ""
                    if self.should_execute_sql(sql_text):
                        cursor.execute(sql_text)
                    else:
                        status = "Not a valid query"
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
                        f"XID:{transaction.xid}, Query: {idx + 1}/{len(transaction.queries)}{substatement_txt}: {err}",
                        exc_info=True,
                    )
                    self.error_logger.append(
                        parse_error(
                            err,
                            transaction.username,
                            self.config["target_cluster_endpoint"].split("/")[-1],
                            query.text,
                        )
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
            self.thread_stats["transaction_error_log"][transaction.get_base_filename()] = errors

    def should_execute_sql(self, sql_text):
        return sql_text is not None and (
            (
                self.config.get("execute_copy_statements", "") == "true"
                and "from 's3:" in sql_text.lower()
            )
            or (
                self.config.get("execute_unload_statements", "") == "true"
                and "to 's3:" in sql_text.lower()
                and self.config["replay_output"] is not None
            )
            or ("from 's3:" not in sql_text.lower())
            and ("to 's3:" not in sql_text.lower())
        )


def categorize_error(err_code):
    # https://www.postgresql.org/docs/current/errcodes-appendix.html
    err_class = {
        "00": "Successful Completion",
        "01": "Warning",
        "02": "No Data",
        "03": "SQL Statement Not Yet Complete",
        "08": "Connection Exception",
        "09": "Triggered Action Exception",
        "0A": "Feature Not Supported",
        "0B": "Invalid Transaction Initiation",
        "0F": "Locator Exception",
        "0L": "Invalid Grantor",
        "0P": "Invalid Role Specification",
        "0Z": "Diagnostics Exception",
        "20": "Case Not Found",
        "21": "Cardinality Violation",
        "22": "Data Exception",
        "23": "Integrity Constraint Violation",
        "24": "Invalid Cursor State",
        "25": "Invalid Transaction State",
        "26": "Invalid SQL Statement Name",
        "27": "Triggered Data Change Violation",
        "28": "Invalid Authorization Specification",
        "2B": "Dependent Privilege Descriptors Still Exist",
        "2D": "Invalid Transaction Termination",
        "2F": "SQL Routine Exception",
        "34": "Invalid Cursor Name",
        "38": "External Routine Exception",
        "39": "External Routine Invocation Exception",
        "3B": "Savepoint Exception",
        "3D": "Invalid Catalog Name",
        "3F": "Invalid Schema Name",
        "40": "Transaction Rollback",
        "42": "Syntax Error or Access Rule Violation",
        "44": "WITH CHECK OPTION Violation",
        "53": "Insufficient Resources",
        "54": "Program Limit Exceeded",
        "55": "Object Not In Prerequisite State",
        "57": "Operator Intervention",
        "58": "System Error",
        "72": "Snapshot Failure",
        "F0": "Configuration File Error",
        "HV": "Foreign Data Wrapper Error (SQL/MED)",
        "P0": "PL/pgSQL Error",
        "XX": "Internal Error",
    }
    if err_code[0:2] in err_class.keys():
        return err_class[err_code[0:2]]

    return "Uncategorized Error"


def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, string)


def parse_error(error, user, db, query_text):
    err_entry = {
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec="seconds"),
        "user": user,
        "db": db,
        "query_text": remove_comments(query_text),
    }

    temp = error.__str__().replace('"', r"\"")
    raw_error_string = json.loads(temp.replace("'", '"'))
    err_entry["detail"] = ""

    if "D" in raw_error_string:
        detail_string = raw_error_string["D"]
        detail = (
            detail_string[detail_string.find("context:") : detail_string.find("query")]
            .split(":", maxsplit=1)[-1]
            .strip()
        )
        err_entry["detail"] = detail

    err_entry["code"] = raw_error_string["C"]
    err_entry["message"] = raw_error_string["M"]
    err_entry["severity"] = raw_error_string["S"]
    err_entry["category"] = categorize_error(err_entry["code"])

    return err_entry
