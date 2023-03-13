import logging
import random
import string
import sys

import dateutil.parser
import re

from copy_replacements_parser import parse_copy_replacements
from common.util import retrieve_compressed_json, matches_filters, get_connection_key

logger = logging.getLogger("SimpleReplayLogger")


class TransactionsParser:
    def __init__(self, config, replay_id):
        self.config = config
        self.workload_directory = config["workload_location"]
        self.filters = config["filters"]
        self.execute_copy_statements = config["execute_copy_statements"]
        self.execute_unload_statements = config["execute_unload_statements"]
        self.replay_id = replay_id

    def parse_transactions(self):
        transactions = []
        gz_path = self.workload_directory.rstrip("/") + "/SQLs.json.gz"

        replacements = []
        if self.execute_copy_statements.lower() == 'true':
            replacements = parse_copy_replacements(self.workload_directory)

        sql_json = retrieve_compressed_json(gz_path)
        for xid, transaction_dict in sql_json["transactions"].items():
            transaction = self.parse_transaction(transaction_dict, replacements)
            if transaction.start_time() and matches_filters(transaction, self.filters):
                transactions.append(transaction)

        transactions.sort(key=lambda txn: (txn.start_time(), txn.xid))

        return transactions

    def parse_transaction(self, transaction_dict, replacements):
        queries = []

        for q in transaction_dict["queries"]:
            start_time = dateutil.parser.isoparse(q["record_time"])
            if q["start_time"] is not None:
                start_time = dateutil.parser.isoparse(q["start_time"])
            end_time = dateutil.parser.isoparse(q["record_time"])
            if q["end_time"] is not None:
                end_time = dateutil.parser.isoparse(q["end_time"])
            if (
                self.execute_copy_statements.lower() == 'true'
                and "copy " in q["text"].lower()
                and "from 's3:" in q["text"].lower()
            ):
                q["text"] = self.get_copy_replacement(q["text"], replacements)
            if (
                self.execute_unload_statements.lower() == 'true'
                and ("unload" in q["text"].lower() and "to 's3:" in q["text"].lower())
                and self.config["unload_iam_role"]
                and self.config["replay_output"].startswith("s3://")
            ):
                q["text"] = self.get_unload_replacements(
                    q["text"],
                    self.config["replay_output"],
                    self.replay_id,
                    self.config["unload_iam_role"],
                )
            if "create user" in q["text"].lower():
                random_password = "".join(
                    random.choices(
                        string.ascii_uppercase + string.ascii_lowercase + string.digits,
                        k=61,
                    )
                )
                q["text"] = re.sub(
                    r"PASSWORD '\*\*\*'",
                    f"PASSWORD '{random_password}aA0'",
                    q["text"],
                    flags=re.IGNORECASE,
                )

            queries.append(Query(start_time, end_time, q["text"]))

        queries.sort(key=lambda query: query.start_time)
        transaction_key = get_connection_key(
            transaction_dict["db"], transaction_dict["user"], transaction_dict["pid"]
        )
        return Transaction(
            transaction_dict["time_interval"],
            transaction_dict["db"],
            transaction_dict["user"],
            transaction_dict["pid"],
            transaction_dict["xid"],
            queries,
            transaction_key,
        )

    @staticmethod
    def get_unload_replacements(query_text, replay_output, replay_name, unload_iam_role):
        to_text = re.search(r"to 's3:\/\/[^']*", query_text, re.IGNORECASE).group()[9:]

        if to_text:
            existing_unload_location = re.search(
                r"to 's3:\/\/[^']*", query_text, re.IGNORECASE
            ).group()[4:]
            replacement_unload_location = replay_output + "/" + replay_name + "/UNLOADs/" + to_text

            new_query_text = query_text.replace(
                existing_unload_location, replacement_unload_location
            )
            if not new_query_text == query_text:
                query_text = new_query_text
                query_text = re.sub(
                    r"IAM_ROLE 'arn:aws:iam::\d+:role/\S+'",
                    f" IAM_ROLE '{unload_iam_role}'",
                    query_text,
                    flags=re.IGNORECASE,
                )
                query_text = re.sub(
                    r"credentials ''",
                    " IAM_ROLE '%s'" % unload_iam_role,
                    query_text,
                    flags=re.IGNORECASE,
                )
                query_text = re.sub(
                    r"with credentials as ''",
                    " IAM_ROLE '%s'" % unload_iam_role,
                    query_text,
                    flags=re.IGNORECASE,
                )
                query_text = re.sub(
                    r"IAM_ROLE ''",
                    " IAM_ROLE '%s'" % unload_iam_role,
                    query_text,
                    flags=re.IGNORECASE,
                )
                query_text = re.sub(
                    r"ACCESS_KEY_ID '' SECRET_ACCESS_KEY '' SESSION_TOKEN ''",
                    " IAM_ROLE '%s'" % unload_iam_role,
                    query_text,
                    flags=re.IGNORECASE,
                )
                query_text = re.sub(
                    r"ACCESS_KEY_ID '' SECRET_ACCESS_KEY ''",
                    " IAM_ROLE '%s'" % unload_iam_role,
                    query_text,
                    flags=re.IGNORECASE,
                )
        return query_text

    @staticmethod
    def get_copy_replacement(query_text, replacements):
        from_text = re.search(r"from 's3:\/\/[^']*", query_text, re.IGNORECASE)
        if from_text:
            existing_copy_location = from_text.group()[6:]

            try:
                replacement_copy_location = replacements[existing_copy_location][0]
            except KeyError:
                logger.info(f"No COPY replacement found for {existing_copy_location}")
                return

            if not replacement_copy_location:
                replacement_copy_location = existing_copy_location

            replacement_copy_iam_role = replacements[existing_copy_location][1]
            if not replacement_copy_iam_role:
                logger.error(
                    f"COPY replacement {existing_copy_location} is missing IAM role or "
                    f"credentials in copy_replacements.csv. Please add credentials or remove replacement."
                )
                sys.exit(-1)

            query_text = query_text.replace(existing_copy_location, replacement_copy_location)

            iam_replacements = [
                (
                    r"IAM_ROLE 'arn:aws:iam::\d+:role/\S+'",
                    f" IAM_ROLE '{replacement_copy_iam_role}'",
                ),
                (r"credentials ''", f" IAM_ROLE '{replacement_copy_iam_role}'"),
                (r"with credentials as ''", f" IAM_ROLE '{replacement_copy_iam_role}'"),
                (r"IAM_ROLE ''", f" IAM_ROLE '{replacement_copy_iam_role}'"),
                (
                    r"ACCESS_KEY_ID '' SECRET_ACCESS_KEY '' SESSION_TOKEN ''",
                    f" IAM_ROLE '{replacement_copy_iam_role}'",
                ),
                (
                    r"ACCESS_KEY_ID '' SECRET_ACCESS_KEY ''",
                    f" IAM_ROLE '{replacement_copy_iam_role}'",
                ),
            ]

            for r in iam_replacements:
                query_text = re.sub(r[0], r[1], query_text, flags=re.IGNORECASE)
        return query_text


class Transaction:
    def __init__(self, time_interval, database_name, username, pid, xid, queries, transaction_key):
        self.time_interval = time_interval
        self.database_name = database_name
        self.username = username
        self.pid = pid
        self.xid = xid
        self.queries = queries
        self.transaction_key = transaction_key

    def __str__(self):
        return (
            "Time interval: %s, Database name: %s, Username: %s, PID: %s, XID: %s, Num queries: %s"
            % (
                self.time_interval,
                self.database_name,
                self.username,
                self.pid,
                self.xid,
                len(self.queries),
            )
        )

    def get_base_filename(self):
        return self.database_name + "-" + self.username + "-" + self.pid + "-" + self.xid

    def start_time(self):
        return self.queries[0].start_time

    def end_time(self):
        return self.queries[-1].end_time

    def offset_ms(self, replay_start_time):
        return self.queries[0].offset_ms(replay_start_time)

    @staticmethod
    def supported_filters():
        return {"database_name", "username", "pid"}


class Query:
    def __init__(self, start_time, end_time, text):
        self.start_time = start_time
        self.end_time = end_time
        self.time_interval = 0
        self.text = text

    def __str__(self):
        return "Start time: %s, End time: %s, Time interval: %s, Text: %s" % (
            self.start_time.isoformat(),
            self.end_time.isoformat(),
            self.time_interval,
            self.text.strip(),
        )

    def offset_ms(self, ref_time):
        return (self.start_time - ref_time).total_seconds() * 1000.0