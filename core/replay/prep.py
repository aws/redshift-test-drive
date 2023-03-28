import copy
import datetime
import logging
import os
import re
import time

import boto3
from boto3 import client
from botocore.exceptions import NoCredentialsError

from core.replay.transactions_parser import TransactionsParser
from core.replay.connections_parser import parse_connections
from common.util import (
    get_connection_key,
    is_serverless,
    CredentialsException,
)
from common.aws_service import get_secret, redshift_get_cluster_credentials

logger = logging.getLogger("WorkloadReplicatorLogger")


# exception thrown if any filters are invalid
class InvalidFilterException(Exception):
    pass


class ReplayPrep:
    def __init__(self, config):
        self.config = config
        self.credentials_cache = {}
        self.boto3_session = boto3.Session()

    def correlate_transactions_with_connections(self, replay_id):
        (connection_logs, total_connections) = parse_connections(
            self.config["workload_location"],
            self.config["time_interval_between_transactions"],
            self.config["time_interval_between_queries"],
            self.config["filters"],
        )
        logger.info(
            f"Found {total_connections} total connections, {total_connections - len(connection_logs)} "
            f"are excluded by filters. Replaying {len(connection_logs)}."
        )

        # Associate transactions with connections
        logger.info(
            f"Loading transactions from {self.config['workload_location']}, this might take some time."
        )
        # group all connections by connection key
        connection_idx_by_key = {}
        for idx, c in enumerate(connection_logs):
            connection_key = get_connection_key(c.database_name, c.username, c.pid)
            connection_idx_by_key.setdefault(connection_key, []).append(idx)

        tp = TransactionsParser(self.config, replay_id)
        all_transactions = tp.parse_transactions()
        transaction_count = len(all_transactions)
        query_count = 0
        # assign the correct connection to each transaction by looking at the most
        # recent connection prior to the transaction start. This relies on connections
        # being sorted.
        first_event_time = datetime.datetime.now(tz=datetime.timezone.utc)
        last_event_time = datetime.datetime.utcfromtimestamp(0).replace(
            tzinfo=datetime.timezone.utc
        )
        for idx, t in enumerate(all_transactions):
            connection_key = get_connection_key(t.database_name, t.username, t.pid)
            possible_connections = connection_idx_by_key[connection_key]
            best_match_idx = None
            for c_idx in possible_connections:
                # truncate session start time, since query/transaction time is truncated to seconds
                if (
                    connection_logs[c_idx].session_initiation_time.replace(
                        microsecond=0
                    )
                    > t.start_time()
                ):
                    break
                best_match_idx = c_idx
            if best_match_idx is None:
                logger.warning(
                    f"Couldn't find matching connection in {len(possible_connections)} connections for transaction {t}, skipping"
                )
                continue
            connection = connection_logs[best_match_idx]
            connection.transactions.append(t)
            if (
                connection.session_initiation_time
                and connection.session_initiation_time < first_event_time
            ):
                first_event_time = connection.session_initiation_time
            if (
                connection.disconnection_time
                and connection.disconnection_time > last_event_time
            ):
                last_event_time = connection.disconnection_time
            if (
                connection.time_interval_between_queries
                or t.time_interval.lower() == "true"
            ):
                for index, sql in enumerate(t.queries[1:]):
                    prev_sql = t.queries[index]
                    prev_sql.time_interval = (
                        sql.start_time - prev_sql.end_time
                    ).total_seconds()
            query_count += len(t.queries)
        logger.info(f"Found {transaction_count} transactions, {query_count} queries")
        logger.info(
            f"{len(connection_logs)} connections contain transactions and will be replayed "
        )
        return (
            connection_logs,
            query_count,
            transaction_count,
            first_event_time,
            last_event_time,
            total_connections,
        )

    def get_connection_credentials(
        self, username, database=None, max_attempts=10, skip_cache=False
    ):
        credentials_timeout_sec = 3600
        retry_delay_sec = 10

        # how long to cache credentials per user
        cache_timeout_sec = 1800

        # check the cache
        if not skip_cache and self.credentials_cache.get(username) is not None:
            record = self.credentials_cache.get(username)
            if (
                datetime.datetime.now(tz=datetime.timezone.utc) - record["last_update"]
            ).total_seconds() < cache_timeout_sec:
                logger.debug(f"Using {username} credentials from cache")
                return record["target_cluster_urls"]
            del self.credentials_cache[username]

        cluster_endpoint = self.config["target_cluster_endpoint"]
        odbc_driver = self.config["odbc_driver"]

        cluster_endpoint_split = cluster_endpoint.split(".")
        cluster_id = f"redshift-serverless-{cluster_endpoint_split[0]}" if is_serverless(self.config) \
            else cluster_endpoint_split[0]
        cluster_region = self.config.get("target_cluster_region", cluster_endpoint_split[2])

        # Keeping NLB just for Serverless for now
        if self.config.get("nlb_nat_dns", None) is not None and is_serverless(self.config):
            cluster_host = self.config["nlb_nat_dns"]
        else:
            cluster_host = cluster_endpoint.split(":")[0]

        cluster_port = cluster_endpoint_split[5].split("/")[0][4:]
        database = cluster_endpoint_split[5].split("/")[1]

        additional_args = {}
        if os.environ.get("ENDPOINT_URL"):
            import urllib3

            # disable insecure warnings when testing endpoint is used
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            additional_args = {
                "endpoint_url": os.environ.get("ENDPOINT_URL"),
                "verify": False,
            }

        response = None

        if is_serverless(self.config) and self.config.get("secret_name", None) is not None:
            logger.info(f"Fetching secrets from: {self.config['secret_name']}")
            secret_keys = ["admin_username", "admin_password"]
            secret_name = get_secret(
                self.config["secret_name"], self.config["target_cluster_region"]
            )
            if len(set(secret_keys) - set(secret_name.keys())) == 0:
                response = {
                    "DbUser": secret_name["admin_username"],
                    "DbPassword": secret_name["admin_password"],
                }
            else:
                logger.error(f"Required secrets not found: {secret_keys}")
                exit(-1)
        else:
            response = redshift_get_cluster_credentials(
                region=cluster_region,
                user=username,
                database_name=database,
                cluster_id=cluster_id,
                duration=credentials_timeout_sec,
                auto_create=False
            )

        if response is None:
            msg = f"Failed to retrieve credentials for {username}"
            raise CredentialsException(msg)

        db_user = response["DbUser"]
        db_password = response["DbPassword"]

        cluster_odbc_url = "Driver={}; Server={}; Database={}; IAM=1; DbUser={}; DbPassword={}; Port={}".format(
            odbc_driver,
            cluster_host,
            database,
            db_user.split(":")[1] if ":" in db_user else db_user,
            db_password,
            cluster_port,
        )

        cluster_psql = {
            "username": db_user,
            "password": db_password,
            "host": cluster_host,
            "port": cluster_port,
            "database": database,
        }

        credentials = {  # old params
            "odbc": cluster_odbc_url,
            "psql": cluster_psql,
            # new params
            "username": db_user,
            "password": db_password,
            "host": cluster_host,
            "port": cluster_port,
            "database": database,
            "odbc_driver": self.config["odbc_driver"],
        }
        logger.debug(
            "Successfully retrieved database credentials for {}".format(username)
        )
        self.credentials_cache[username] = {
            "last_update": datetime.datetime.now(tz=datetime.timezone.utc),
            "target_cluster_urls": credentials,
        }
        return credentials

    @staticmethod
    def validate_and_normalize_filters(obj, filters):
        """validate filters and set defaults. The object just needs to
        provide a supported_filters() function."""

        normalized_filters = copy.deepcopy(filters)

        if "include" not in normalized_filters:
            normalized_filters["include"] = {}
        if "exclude" not in normalized_filters:
            normalized_filters["exclude"] = {}

        for f in obj.supported_filters():
            normalized_filters["include"].setdefault(f, ["*"])
            normalized_filters["exclude"].setdefault(f, [])

        include_overlap = set(normalized_filters["include"].keys()) - set(
            obj.supported_filters()
        )
        if len(include_overlap) > 0:
            raise InvalidFilterException(f"Unknown filters: {include_overlap}")

        exclude_overlap = set(normalized_filters["exclude"].keys()) - set(
            obj.supported_filters()
        )
        if len(exclude_overlap) > 0:
            raise InvalidFilterException(f"Unknown filters: {exclude_overlap}")

        for f in obj.supported_filters():
            include = normalized_filters["include"][f]
            exclude = normalized_filters["exclude"][f]

            if len(include) == 0:
                raise InvalidFilterException("Include filter must not be empty")

            overlap = set(include).intersection(set(exclude))
            if len(overlap) > 0:
                raise InvalidFilterException(
                    f"Can't include the same values in both include and exclude for filter: "
                    f"{overlap}"
                )

            for x in (include, exclude):
                if len(x) > 1 and "*" in x:
                    raise InvalidFilterException(
                        "'*' can not be used with other filter values filter"
                    )

        return normalized_filters

    @staticmethod
    def parse_filename(filename):
        # Try to parse the info from the filename. Filename format is:
        #  {database_name}-{username}-{pid}-{xid}
        # Both database_name and username can contain "-" characters.  In that case, we'll
        # take a guess that the - is in the username rather than the database name.
        match = re.search(r"^([^-]+)-(.+)-(\d+)-(\d+)", filename)
        if not match:
            return None, None, None, None
        return match.groups()
