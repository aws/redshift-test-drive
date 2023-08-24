import csv
import datetime
import hashlib
import logging
import sys
import os
import traceback
import zipfile
import yaml
import common.config as config_helper
import common.log as log_helper
from connections_parser import ConnectionLog
from core.replay.prep import ReplayPrep
from summarizer import summarize
from replayer import Replayer
from common.util import (
    cluster_dict,
    is_serverless,
    CredentialsException,
    bucket_dict,
)
import report_gen
from unload_sys_table import UnloadSysTable
import common.aws_service as aws_service_helper

logger = logging.getLogger("WorkloadReplicatorLogger")


# exception thrown if cluster doesn't exist
class ClusterNotExist(Exception):
    pass


def main():
    # Parse config file
    config = config_helper.get_config_file_from_args()
    config_helper.validate_config_for_replay(config)

    is_serverless_endpoint = is_serverless(config)

    cluster = cluster_dict(config["target_cluster_endpoint"], is_serverless_endpoint)

    replay_start_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    logger.info(f"Replay start time: {replay_start_timestamp}")

    id_hash = hashlib.sha1(replay_start_timestamp.isoformat().encode("UTF-8")).hexdigest()[:5]
    if config.get("tag", "") != "":
        replay_id = (
            f'{replay_start_timestamp.isoformat()}_{cluster.get("id")}_{config["tag"]}_{id_hash}'
        )
    else:
        replay_id = f'{replay_start_timestamp.isoformat()}_{cluster.get("id")}_{id_hash}'

    # Setup Logging
    level = logging.getLevelName(config.get("log_level", "INFO").upper())
    log_helper.init_logging(
        "replay_log",
        dir=f"core/logs/replay/replay_log-{replay_id}",
        level=level,
        preamble=yaml.dump(config),
        backup_count=config.get("backup_count", 5),
        script_type="replay",
        log_id=replay_id,
        replace_if_exists=False
    )
    log_helper.log_version()

    if not config["replay_output"]:
        config["replay_output"] = None

    prep = ReplayPrep(config)
    config["filters"] = ReplayPrep.validate_and_normalize_filters(
        ConnectionLog, config.get("filters", {})
    )
    (
        connection_logs,
        query_count,
        transaction_count,
        first_event_time,
        last_event_time,
        total_connections,
    ) = prep.correlate_transactions_with_connections(replay_id)

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
        replayer = Replayer(config)
        aggregated_stats = replayer.start_replay(
            connection_logs,
            first_event_time,
            query_count,
            replay_start_timestamp,
            replay_id,
        )
        complete = True
    except KeyboardInterrupt:
        replay_id += "_INCOMPLETE"
        logger.warning("Got CTRL-C, exiting...")
    except Exception as e:
        replay_id += "_INCOMPLETE"
        logger.error(f"Replay terminated. {e}")
        logger.debug("".join(traceback.format_exception(*sys.exc_info())))
        raise e

    if len(errors) > 0:
        bucket = bucket_dict(config["analysis_output"])
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
        config,
        replay_start_timestamp,
        aggregated_stats,
        query_count,
        replay_id,
        transaction_count,
        replay_end_time,
    )

    if config.get("analysis_iam_role") and config.get("analysis_output"):
        try:
            report_gen.replay_pdf_generator(
                replay=replay_id,
                cluster_endpoint=config["target_cluster_endpoint"],
                start_time=replay_start_timestamp,
                end_time=replay_end_time,
                bucket_url=config["analysis_output"],
                iam_role=config["analysis_iam_role"],
                user=config["master_username"],
                tag=config["tag"],
                workload=config["workload_location"],
                is_serverless=is_serverless_endpoint,
                secret_name=config["secret_name"],
                nlb_nat_dns=config["nlb_nat_dns"],
                complete=complete,
                summary=replay_summary,
            )
        except Exception as e:
            logger.error(f"Could not complete replay analysis. {e}")
            logger.debug("".join(traceback.format_exception(*sys.exc_info())))
    else:
        logger.info("Analysis not enabled for this replay.")

    if (
        config["replay_output"]
        and config["unload_system_table_queries"]
        and config["target_cluster_system_table_unload_iam_role"]
    ):
        logger.info(f'Exporting system tables to {config["replay_output"]}')

        unload_table = UnloadSysTable(config, replay_id)
        unload_table.unload_system_table()

        logger.info(f'Exported system tables to {config["replay_output"]}')

    # uploading replay logs to s3

    bucket = bucket_dict(config["workload_location"])
    object_key = "replay_logs.zip"
    zip_file_name = f"replay_logs.zip"
    if bucket.get("bucket_name", ""):
        logger.info(f"Uploading replay logs to {bucket['bucket_name']}/{bucket['prefix']}")
        dir = f"core/logs/replay/replay_log-{replay_id}"
        with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zip_object:
            for folder_name, sub_folders, file_names in os.walk(dir):
                for filename in file_names:
                    file_path = os.path.join(folder_name, filename)
                    zip_object.write(file_path)
        with open(zip_file_name, "rb") as f:
            aws_service_helper.s3_put_object(
                f, bucket["bucket_name"], f"{bucket['prefix']}{object_key}"
            )
    else:
        logger.info("Invalid bucket name")


if __name__ == "__main__":
    main()
