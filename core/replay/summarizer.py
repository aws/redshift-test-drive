import datetime
import logging
import os
from tqdm import tqdm

from boto3 import client

import common.aws_service as aws_service_helper

logger = logging.getLogger("WorkloadReplicatorLogger")


def summarize(
    connection_logs,
    config,
    replay_start_timestamp,
    aggregated_stats,
    query_count,
    replay_id,
    transaction_count,
    replay_end_time,
):
    replay_summary = []
    logger.info("Replay summary:")
    replay_summary.append(
        f"Attempted to replay {query_count} queries, {transaction_count} transactions, "
        f"{len(connection_logs)} connections."
    )
    try:
        replay_summary.append(
            f"Successfully replayed {aggregated_stats.get('transaction_success', 0)} out of {transaction_count} "
            f"({round((aggregated_stats.get('transaction_success', 0) / transaction_count) * 100)}%) transactions."
        )
        replay_summary.append(
            f"Successfully replayed {aggregated_stats.get('query_success', 0)} out of {query_count} "
            f"({round((aggregated_stats.get('query_success', 0) / query_count) * 100)}%) queries."
        )
    except ZeroDivisionError:
        pass
    error_location = config.get("error_location", config["workload_location"])
    replay_summary.append(
        f"Encountered {len(aggregated_stats['connection_error_log'])} "
        f"connection errors and {len(aggregated_stats['transaction_error_log'])} transaction errors"
    )
    # and save them
    export_errors(
        aggregated_stats["connection_error_log"],
        aggregated_stats["transaction_error_log"],
        error_location,
        replay_id,
    )
    replay_summary.append(f"Replay finished in {replay_end_time - replay_start_timestamp}.")
    for line in replay_summary:
        logger.info(line)
    logger.info(
        f"Replay finished in {datetime.datetime.now(tz=datetime.timezone.utc) - replay_start_timestamp}."
    )
    return replay_summary


def export_errors(connection_errors, transaction_errors, workload_location, replay_name):
    """Save any errors that occurred during replay to a local directory or s3"""

    if len(connection_errors) == len(transaction_errors) == 0:
        logger.info("No errors, nothing to save")
        return

    logger.info(
        f"Saving {len(connection_errors)} connection errors, {len(transaction_errors)} transaction_errors"
    )

    connection_error_location = workload_location + "/" + replay_name + "/connection_errors"
    transaction_error_location = workload_location + "/" + replay_name + "/transaction_errors"



    if workload_location.startswith("s3://"):
        workload_s3_location = workload_location[5:].partition("/")
        bucket_name = workload_s3_location[0]
        prefix = workload_s3_location[2]
        s3_client = client("s3")
    else:
        os.makedirs(connection_error_location)
        os.makedirs(transaction_error_location)

    logger.info(f"Exporting connection errors to {connection_error_location}/")
    bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}{postfix}]"
    for filename, connection_error_text in tqdm(
            connection_errors.items(),
            disable=False,
            unit="files",
            desc="Files processed",
            bar_format=bar_format,
        ):
    
        if workload_location.startswith("s3://"):
            if prefix:
                key_loc = "%s/%s/connection_errors/%s.txt" % (
                    prefix,
                    replay_name,
                    filename,
                )
            else:
                key_loc = "%s/connection_errors/%s.txt" % (replay_name, filename)
            aws_service_helper.s3_put_object(connection_error_text,bucket_name, key_loc)
        else:
            error_file = open(connection_error_location + "/" + filename + ".txt", "w")
            error_file.write(connection_error_text)
            error_file.close()

    logger.info(f"Exporting transaction errors to {transaction_error_location}/")
    for filename, transaction_errors in tqdm(
            transaction_errors.items(),
            disable=False,
            unit="files",
            desc="Files processed",
            bar_format=bar_format,
        ):
        error_file_text = ""
        for transaction_error in transaction_errors:
            error_file_text += f"{transaction_error[0]}\n{transaction_error[1]}\n\n"

        if workload_location.startswith("s3://"):
            if prefix:
                key_loc = "%s/%s/transaction_errors/%s.txt" % (
                    prefix,
                    replay_name,
                    filename,
                )
            else:
                key_loc = "%s/transaction_errors/%s.txt" % (replay_name, filename)
            s3_client.put_object(
                Body=error_file_text,
                Bucket=bucket_name,
                Key=key_loc,
            )
        else:
            error_file = open(transaction_error_location + "/" + filename + ".txt", "w")
            error_file.write(error_file_text)
            error_file.close()
