import logging
import sys
import hashlib
import datetime
import yaml
import os
import zipfile
import time
import common.config as config_helper
import common.log as log_helper
from common import aws_service as aws_service_helper
from common.util import cluster_dict, db_connect
import core.extract.extractor as extractor

logger = logging.getLogger("WorkloadReplicatorLogger")


def main():

    extract_start_time = time.time()

    # Parse config file
    config = config_helper.get_config_file_from_args()
    config_helper.validate_config_file_for_extract(config)

    # UID for extract logs
    extract_start_timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
    id_hash = hashlib.sha1(
        extract_start_timestamp.isoformat().encode("UTF-8")
    ).hexdigest()[:5]
    if config.get("source_cluster_endpoint", "") != "":
        cluster = cluster_dict(config["source_cluster_endpoint"])
        if config.get("tag", "") != "":
            extract_id = f'{extract_start_timestamp.isoformat()}_{cluster.get("id")}_{config["tag"]}_{id_hash}'
        else:
            extract_id = (
                f'{extract_start_timestamp.isoformat()}_{cluster.get("id")}_{id_hash}'
            )
    else:
        log_location = config.get("log_location")
        if config.get("tag", "") != "":
            extract_id = f'{extract_start_timestamp.isoformat()}_{log_location}_{config["tag"]}_{id_hash}'
        else:
            extract_id = (
                f"{extract_start_timestamp.isoformat()}_{log_location}_{id_hash}"
            )

    # Setup Logging
    level = logging.getLevelName(config.get("log_level", "INFO").upper())
    log_helper.init_logging(
        "extract.log",
        dir=f"core/logs/extract/extract_log-{extract_id}",
        level=level,
        preamble=yaml.dump(config),
        backup_count=config.get("backup_count", 2),
        script_type="extract",
        log_id=extract_id,
    )
    log_helper.log_version()

    e = extractor.Extractor(config)
    if not e.load_driver():
        sys.exit("Failed to load driver")

    # setting application name for tracking
    application = "WorkloadReplicator-Extract"
    
    host = config.get("source_cluster_endpoint").split(".")[0]
    port = int(config.get("source_cluster_endpoint").split(":")[-1].split("/")[0])
    DbUser = config.get("master_username")
    DbName = config.get("source_cluster_endpoint").split("/")[-1]
    region = config.get("region")
    endpoint = config.get('source_cluster_endpoint').split(":")[0]

    response = aws_service_helper.redshift_get_cluster_credentials(
        user=DbUser,
        database_name=DbName,
        cluster_id=host,
        region=region)
    db_connect(host=endpoint,
               port=port,
               database=DbName,
               password=response['DbPassword'],
               username=response['DbUser'], app_name=application)

    # Run extract job
    (
        extraction_name,
        start_time,
        end_time,
        log_location,
    ) = e.get_parameters_for_log_extraction()
    (connections, audit_logs, databases, last_connections) = e.get_extract(
        log_location, start_time, end_time
    )

    e.validate_log_result(connections, audit_logs)
    e.retrieve_cluster_endpoint_info(extraction_name)

    e.save_logs(
        audit_logs,
        last_connections,
        config["workload_location"] + "/" + extraction_name,
        connections,
        start_time,
        end_time,
    )

    # save the extract logs to S3
    output_directory = f'{config["workload_location"]+ "/" + extraction_name}'
    if output_directory.startswith("s3://"):
        output_s3_location = output_directory[5:].partition("/")
        bucket_name = output_s3_location[0]
        output_prefix = output_s3_location[2]
        object_key = "extract_logs.zip"
        zip_file_name = f"extract_logs.zip"
        logger.info(f"Uploading extract logs to {bucket_name}/{output_prefix}")
        dir = f"core/logs/extract/extract_log-{extract_id}"
        with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zip_object:
            for folder_name, sub_folders, file_names in os.walk(dir):
                for filename in file_names:
                    file_path = os.path.join(folder_name, filename)
                    zip_object.write(file_path)
        with open(zip_file_name, "rb") as f:
            aws_service_helper.s3_put_object(
                f, bucket_name, f"{output_prefix}/{object_key}"
            )

    total_extract_time = str(datetime.timedelta(seconds=(time.time() - extract_start_time)))
    logger.info(f"Extract completed in {total_extract_time}")

if __name__ == "__main__":
    main()
