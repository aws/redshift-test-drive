import csv
import datetime
import hashlib
import logging
import re
import sys
import yaml
import common.config as config_helper
import common.log as log_helper
from connections_parser import ConnectionLog
from prep import ReplayPrep
from summarizer import summarize
from replayer import Replayer
from common.util import (
    db_connect,
    cluster_dict,
    is_serverless,
    CredentialsException,
    bucket_dict,
)
from tools.replay_analysis.replay_analysis import run_replay_analysis
from unload_sys_table import UnloadSysTable
import common.aws_service as aws_service_helper

g_total_connections = 0
g_queries_executed = 0
g_exit = False

g_config = {}

g_replay_timestamp = None

g_is_serverless = False
g_serverless_cluster_endpoint_pattern = (
    r"(.+)\.(.+)\.(.+).redshift-serverless(-dev)?\.amazonaws\.com:[0-9]{4}\/(.)+"
)

logger = logging.getLogger("SimpleReplayLogger")


# exception thrown if cluster doesn't exist
class ClusterNotExist(Exception):
    pass


def main():
    # Parse config file
    global g_config
    g_config = config_helper.get_config_file_from_args()
    config_helper.validate_config_for_replay(g_config)

    # Setup Logging
    level = logging.getLevelName(g_config.get("log_level", "INFO").upper())
    log_helper.init_logging(
        "replay.log",
        level=level,
        preamble=yaml.dump(g_config),
        backup_count=g_config.get("backup_count", 2),
    )
    log_helper.log_version()

    global g_is_serverless

    g_is_serverless = is_serverless(g_config)

    cluster = cluster_dict(g_config["target_cluster_endpoint"], g_is_serverless)

    replay_start_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    logger.info(f"Replay start time: {replay_start_timestamp}")

    id_hash = hashlib.sha1(
        replay_start_timestamp.isoformat().encode("UTF-8")
    ).hexdigest()[:5]
    if g_config.get("tag", "") != "":
        replay_id = (
            f'{replay_start_timestamp.isoformat()}_{cluster.get("id")}_{g_config["tag"]}_{id_hash}'
        )
    else:
        replay_id = (
            f'{replay_start_timestamp.isoformat()}_{cluster.get("id")}_{id_hash}'
        )

    if not g_config["replay_output"]:
        g_config["replay_output"] = None

    prep = ReplayPrep(g_config)
    g_config["filters"] = ReplayPrep.validate_and_normalize_filters(
        ConnectionLog, g_config.get("filters", {})
    )
    (
        connection_logs,
        query_count,
        transaction_count,
        first_event_time,
        last_event_time,
        total_connections,
    ) = prep.correlate_transactions_with_connections(replay_id)

    global g_total_connections
    g_total_connections = len(connection_logs)

    # test connection
    try:
        # use the first user as a test
        prep.get_connection_credentials(
            connection_logs[0].username,
            database=connection_logs[0].database_name,
            max_attempts=1,
        )
    except CredentialsException as e:
        logger.error(
            f"Unable to retrieve credentials using GetClusterCredentials ({str(e)}).  "
            f"Please verify that an IAM policy exists granting access.  See the README for more details."
        )
        sys.exit(-1)

    if len(connection_logs) == 0:
        logger.info("No logs to replay, nothing to do.")
        sys.exit()

    # Actual replay
    logger.debug("Starting replay")
    complete = False
    aggregated_stats = {}
    errors = []
    try:
        replayer = Replayer(g_config)
        aggregated_stats = replayer.start_replay(
            connection_logs, first_event_time, query_count, replay_start_timestamp
        )
        complete = True
    except KeyboardInterrupt:
        replay_id += "_INCOMPLETE"
        logger.warning("Got CTRL-C, exiting...")
    except Exception as e:
        replay_id += "_INCOMPLETE"
        logger.error(f"Replay terminated. {e}")
        raise e

    if len(errors) > 0:
        bucket = bucket_dict(g_config["analysis_output"])
        with open("replayerrors000", "w", newline="") as output_file:
            try:
                dict_writer = csv.DictWriter(output_file, fieldnames=errors[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(errors)
            except Exception as e:
                logger.debug(f"Failed to write replay errors to CSV. {e}")

        try:
            aws_service_helper.s3_upload(
                output_file.name,
                bucket,
                f"{bucket['prefix']}analysis/{replay_id}/raw_data/{output_file.name}",
            )
        except Exception as e:
            logger.debug(f"Error upload to S3 {bucket['bucket_name']} failed. {e}")
    replay_end_time = datetime.datetime.now(tz=datetime.timezone.utc)
    replay_summary = summarize(
        connection_logs,
        g_config,
        replay_start_timestamp,
        aggregated_stats,
        query_count,
        replay_id,
        transaction_count,
        replay_end_time,
    )

    if g_config.get("analysis_iam_role") and g_config.get("analysis_output"):
        try:
            run_replay_analysis(
                replay=replay_id,
                cluster_endpoint=g_config["target_cluster_endpoint"],
                start_time=replay_start_timestamp,
                end_time=replay_end_time,
                bucket_url=g_config["analysis_output"],
                iam_role=g_config["analysis_iam_role"],
                user=g_config["master_username"],
                tag=g_config["tag"],
                workload=g_config["workload_location"],
                is_serverless=g_is_serverless,
                secret_name=g_config["secret_name"],
                nlb_nat_dns=g_config["nlb_nat_dns"],
                complete=complete,
                summary=replay_summary,
            )
        except Exception as e:
            logger.error(f"Could not complete replay analysis. {e}")
    else:
        logger.info("Analysis not enabled for this replay.")

    if (
        g_config["replay_output"]
        and g_config["unload_system_table_queries"]
        and g_config["target_cluster_system_table_unload_iam_role"]
    ):
        logger.info(f'Exporting system tables to {g_config["replay_output"]}')

        unload_table = UnloadSysTable(g_config, replay_id)
        unload_table.unload_system_table()

        logger.info(f'Exported system tables to {g_config["replay_output"]}')


if __name__ == "__main__":
    main()