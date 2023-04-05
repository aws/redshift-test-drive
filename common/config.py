import argparse
import logging
import re

import yaml
import sys
from dateutil import parser

logger = logging.getLogger("WorkloadReplicatorLogger")


def get_config_file_from_args():
    """
    getting the CLI arguments
    :return: CLI argumets
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file",
        type=argparse.FileType("r"),
        help="Location of extraction config file.",
    )
    args = parser.parse_args()
    config_file = args.config_file
    with config_file as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exception:
            sys.exit(f"Failed to parse extraction config yaml file: {exception}")


def validate_config_file_for_extract(config):
    """
    Validates the parameters from extract.yaml file
    :param config: extract.yaml file
    :return:
    """
    if config["source_cluster_endpoint"]:
        if "redshift-serverless" in config["source_cluster_endpoint"]:
            if (
                not len(config["source_cluster_endpoint"].split(".")) == 6
                or not len(config["source_cluster_endpoint"].split(":")) == 2
                or not len(config["source_cluster_endpoint"].split("/")) == 2
            ):
                logger.error(
                    'Config file value for "source_cluster_endpoint" is not a valid endpoint. Endpoints must be in '
                    "the format of <identifier>.<region>.redshift-serverless.amazonaws.com:<port>/<database-name>. "
                )
                exit(-1)
        elif (
            not len(config["source_cluster_endpoint"].split(".")) == 6
            or not len(config["source_cluster_endpoint"].split(":")) == 2
            or not len(config["source_cluster_endpoint"].split("/")) == 2
            or ".redshift.amazonaws.com:" not in config["source_cluster_endpoint"]
        ):
            logger.error(
                'Config file value for "source_cluster_endpoint" is not a valid endpoint. Endpoints must be in the '
                "format of <cluster-name>.<identifier>.<region>.redshift.amazonaws.com:<port>/<database-name>. "
            )
            exit(-1)
        if not config["master_username"]:
            logger.error(
                'Config file missing value for "master_username". Please provide a value or remove the '
                '"source_cluster_endpoint" value. '
            )
            exit(-1)
        if not config["region"]:
            logger.error(
                'Config file missing value for "region". Please provide a value or remove the '
                '"source_cluster_endpoint" value. '
            )
            exit(-1)
    else:
        if not config["log_location"]:
            logger.error(
                'Config file missing value for "log_location". Please provide a value for "log_location", or provide '
                'a value for "source_cluster_endpoint". '
            )
            exit(-1)
    if config["start_time"]:
        try:
            parser.isoparse(config["start_time"])
        except ValueError:
            logger.error(
                'Config file "start_time" value not formatted as ISO 8601. Please format "start_time" as ISO 8601 or '
                "remove its value. "
            )
            exit(-1)
    if config["external_schemas"]:
        try:
            if not isinstance(config["external_schemas"], list):
                raise TypeError
        except TypeError:
            logger.error("external_schemas type not list")
            exit(-1)

    if config["end_time"]:
        try:
            parser.isoparse(config["end_time"])
        except ValueError:
            logger.error(
                'Config file "end_time" value not formatted as ISO 8601. Please format "end_time" as ISO 8601 or '
                "remove its value. "
            )
            exit(-1)
    if not config["workload_location"]:
        logger.error(
            'Config file missing value for "workload_location". Please provide a value for "workload_location".'
        )
        exit(-1)
    if config["source_cluster_system_table_unload_location"] and not config[
        "source_cluster_system_table_unload_location"
    ].startswith("s3://"):
        logger.error(
            'Config file value for "source_cluster_system_table_unload_location" must be an S3 location (starts with '
            '"s3://"). Please remove this value or put in an S3 location. '
        )
        exit(-1)
    if (
        config["source_cluster_system_table_unload_location"]
        and not config["source_cluster_system_table_unload_iam_role"]
    ):
        logger.error(
            'Config file missing value for "source_cluster_system_table_unload_iam_role". Please provide a value for '
            '"source_cluster_system_table_unload_iam_role", or remove the value for '
            '"source_cluster_system_table_unload_location". '
        )
        exit(-1)
    if (
        config["source_cluster_system_table_unload_location"]
        and not config["unload_system_table_queries"]
    ):
        logger.error(
            'Config file missing value for "unload_system_table_queries". Please provide a value for '
            '"unload_system_table_queries", or remove the value for "source_cluster_system_table_unload_location". '
        )
        exit(-1)
    if config["unload_system_table_queries"] and not config[
        "unload_system_table_queries"
    ].endswith(".sql"):
        logger.error(
            'Config file value for "unload_system_table_queries" does not end with ".sql". Please ensure the value '
            'for "unload_system_table_queries" ends in ".sql". See the provided "unload_system_tables.sql" as an '
            "example. "
        )
        exit(-1)


def validate_config_for_replay(config):
    cluster_endpoint_pattern = (
        r"(.+)\.(.+)\.(.+).redshift(-serverless)?\.amazonaws\.com:[0-9]{4}\/(.)+"
    )
    if not bool(
        re.fullmatch(cluster_endpoint_pattern, config["target_cluster_endpoint"])
    ):
        logger.error(
            'Config file value for "target_cluster_endpoint" is not a valid endpoint. Endpoints must be in the format '
            "of <cluster-hostname>:<port>/<database-name>."
        )
        exit(-1)
    if not config["target_cluster_region"]:
        logger.error('Config file value for "target_cluster_region" is required.')
        exit(-1)
    if not config["odbc_driver"]:
        config["odbc_driver"] = None
        logger.debug(
            'Config file missing value for "odbc_driver" so replay will not use ODBC. Please provide a value for '
            '"odbc_driver" to replay using ODBC.'
        )
    if config["odbc_driver"] or config["default_interface"] == "odbc":
        try:
            import pyodbc
        except (ValueError, ImportError):
            logger.error(
                "Import of pyodbc failed. Please install pyodbc library to use ODBC as default driver. Please refer "
                "to REAME.md"
            )
            exit(-1)
    if not (
        config["default_interface"] == "psql" or config["default_interface"] == "odbc"
    ):
        logger.error(
            'Config file value for "default_interface" must be either "psql" or "odbc". Please change the value for '
            '"default_interface" to either "psql" or "odbc".'
        )
        exit(-1)
    if not (
        config["time_interval_between_transactions"] == ""
        or config["time_interval_between_transactions"] == "all on"
        or config["time_interval_between_transactions"] == "all off"
    ):
        logger.error(
            'Config file value for "time_interval_between_transactions" must be either "", "all on", or "all off". '
            'Please change the value for "time_interval_between_transactions" to be "", "all on", or "all off".'
        )
        exit(-1)
    if not (
        config["time_interval_between_queries"] == ""
        or config["time_interval_between_queries"] == "all on"
        or config["time_interval_between_queries"] == "all off"
    ):
        logger.error(
            'Config file value for "time_interval_between_queries" must be either "", "all on", or "all off". Please '
            'change the value for "time_interval_between_queries" to be "", "all on", or "all off".'
        )
        exit(-1)
    if not (
        config["execute_copy_statements"] == "true"
        or config["execute_copy_statements"] == "false"
    ):
        logger.error(
            'Config file value for "execute_copy_statements" must be either "true" or "false". Please change the value '
            'for "execute_copy_statements" to either "true" or "false".'
        )
        exit(-1)
    if not (
        config["execute_unload_statements"] == "true"
        or config["execute_unload_statements"] == "false"
    ):
        logger.error(
            'Config file value for "execute_unload_statements" must be either "true" or "false". Please change the '
            'value for "execute_unload_statements" to either "true" or "false".'
        )
        exit(-1)
    if config["replay_output"] and not config["replay_output"].startswith("s3://"):
        logger.error(
            'Config file value for "replay_output" must be an S3 location (starts with "s3://"). Please remove this '
            "value or put in an S3 location."
        )
        exit(-1)
    if not config["replay_output"] and config["execute_unload_statements"] == "true":
        logger.error(
            'Config file value for "replay_output" is not provided while "execute_unload_statements" is set to true. '
            'Please provide a valid S3 location for "replay_output".'
        )
        exit(-1)
    if (
        config["replay_output"]
        and config["target_cluster_system_table_unload_iam_role"]
        and not config["unload_system_table_queries"]
    ):
        logger.error(
            'Config file missing value for "unload_system_table_queries". Please provide a value for '
            '"unload_system_table_queries", or remove the value for "target_cluster_system_table_unload_iam_role".'
        )
        exit(-1)
    if (
        config["replay_output"]
        and config["target_cluster_system_table_unload_iam_role"]
        and config["unload_system_table_queries"]
        and not config["unload_system_table_queries"].endswith(".sql")
    ):
        logger.error(
            'Config file value for "unload_system_table_queries" does not end with ".sql". Please ensure the value for '
            '"unload_system_table_queries" ends in ".sql". See the provided "unload_system_tables.sql" as an example.'
        )
        exit(-1)
    if not config["workload_location"]:
        logger.error(
            'Config file missing value for "workload_location". Please provide a value for "workload_location".'
        )
        exit(-1)
    if not config["nlb_nat_dns"]:
        config["nlb_nat_dns"] = None
        logger.debug(
            "No NLB / NAT endpoint specified. Replay will use target_cluster_endpoint to connect."
        )
    if not config["secret_name"]:
        config["secret_name"] = None
        logger.debug("SECRET_NAME property not specified.")
