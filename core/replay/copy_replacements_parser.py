import csv
import logging
import sys

import common.aws_service as aws_service_helper

logger = logging.getLogger("WorkloadReplicatorLogger")


def parse_copy_replacements(workload_directory):
    copy_replacements = {}
    replacements_path = workload_directory.rstrip("/") + "/copy_replacements.csv"

    if replacements_path.startswith("s3://"):
        workload_s3_location = replacements_path[5:].partition("/")
        bucket_name = workload_s3_location[0]
        prefix = workload_s3_location[2]
        s3_object = aws_service_helper.s3_client_get_object(bucket_name, prefix)
        csv_string = s3_object["Body"].read().decode("utf-8")
        copy_replacements_reader = csv.reader(csv_string.splitlines())
        next(copy_replacements_reader)  # Skip header
        for row in copy_replacements_reader:
            if len(row) == 3 and row[2]:
                copy_replacements[row[0]] = [row[1], row[2]]
    else:
        with open(replacements_path, "r") as csvfile:
            copy_replacements_reader = csv.reader(csvfile)
            next(copy_replacements_reader)  # Skip header
            for idx, row in enumerate(copy_replacements_reader):
                if len(row) != 3:
                    logger.error(
                        f"Replacements file {replacements_path} is malformed (row {idx}, line:\n{row}"
                    )
                    sys.exit()
                copy_replacements[row[0]] = [row[1], row[2]]

    logger.info(f"Loaded {len(copy_replacements)} COPY replacements from {replacements_path}")
    return copy_replacements
