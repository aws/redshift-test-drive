import re

import logging.handlers
import redshift_connector
from urllib.parse import urlparse
import datetime
import common.aws_service as aws_service_helper

logger = logging.getLogger("WorkloadReplicatorLogger")

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
serverless_cluster_endpoint_pattern = (
    r"(.+)\.(.+)\.(.+).redshift-serverless(-dev)?\.amazonaws\.com:[0-9]{4,5}\/(.)+"
)


def db_connect(
    interface="psql",
    host=None,
    port=5439,
    username=None,
    password=None,
    database=None,
    odbc_driver=None,
    drop_return=False,
    app_name=None
):
    if interface == "psql":
        conn = redshift_connector.connect(
            user=username, password=password, host=host, port=port,
            database=database, application_name=app_name
        )

        # if drop_return is set, monkey patch driver to not store result set in memory
        if drop_return:

            def drop_data(self, data) -> None:
                pass

            # conn.handle_DATA_ROW = drop_data
            conn.message_types[redshift_connector.core.DATA_ROW] = drop_data

    elif interface == "odbc":
        import pyodbc

        if drop_return:
            raise Exception("drop_return not supported for odbc")

        odbc_connection_str = (
            "Driver={}; Server={}; Database={}; IAM=1; DbUser={}; DbPassword={}; Port={}".format(
                odbc_driver, host, database, username, password, port
            )
        )
        conn = pyodbc.connect(odbc_connection_str)
    else:
        raise ValueError(f"Unknown Interface {interface}")
    conn.autocommit = True
    return conn


def cluster_dict(endpoint, is_serverless=False, start_time=None, end_time=None):
    """Create a object-like dictionary from cluster endpoint"""
    parsed = urlparse(endpoint)
    url_split = parsed.scheme.split(".")
    port_database = parsed.path.split("/")

    if is_serverless:
        workgroup_name = url_split[0]

    cluster = {
        "endpoint": endpoint,
        "id": url_split[0],
        "host": parsed.scheme,
        "region": url_split[2],
        "port": port_database[0],
        "database": port_database[1],
        "is_serverless": is_serverless,
    }

    if start_time is not None:
        cluster["start_time"] = start_time
    if end_time is not None:
        cluster["end_time"] = end_time

    if is_serverless:
        try:
            response = aws_service_helper.redshift_get_serverless_workgroup(
                workgroup_name, cluster.get("region")
            )

            cluster["num_nodes"] = "N/A"
            cluster["instance"] = "Serverless"
            cluster["base_rpu"] = response["workgroup"]["baseCapacity"]
        except Exception as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning(
                    f"Serverless endpoint could not be found "
                    f"RedshiftServerless:GetWorkGroup. {e}"
                )
                raise e
            else:
                logger.warning(
                    f"Exception during fetching work group details for Serverless endpoint "
                    f"RedshiftServerless:GetWorkGroup. {e}"
                )
                cluster["num_nodes"] = "N/A"
                cluster["instance"] = "Serverless"
                cluster["base_rpu"] = "N/A"
    else:
        try:
            response = aws_service_helper.redshift_describe_clusters(
                cluster.get("id"), cluster.get("region")
            )

            cluster["num_nodes"] = response["Clusters"][0]["NumberOfNodes"]
            cluster["instance"] = response["Clusters"][0]["NodeType"]
        except Exception as e:
            logger.warning(
                f"Unable to get cluster information. Please ensure IAM permissions include "
                f"Redshift:DescribeClusters. {e}"
            )
            cluster["num_nodes"] = "N/A"
            cluster["instance"] = "N/A"

    return cluster


def bucket_dict(bucket_url):
    bucket, path = None, None
    try:
        parsed = urlparse(bucket_url)
        bucket, path = parsed.netloc, parsed.path
    except ValueError as e:
        logger.error(
            f"{e}\nPlease enter a valid S3 url following one of the following style conventions: "
            f"S3://bucket-name/key-name"
        )
        exit(-1)
    if path.startswith("/"):
        path = path[1:]
    if not path == "" and not path.endswith("/"):
        path = f"{path}/"
    if path == "replays/":
        path = ""
    return {"url": bucket_url, "bucket_name": bucket, "prefix": path}


def matches_filters(obj, filters):
    """Check if the object matches the filters.  The object just needs to
    provide a supported_filters() function.  This also assumes filters has already
    been validated"""

    included = 0
    for field in obj.supported_filters():
        include = filters["include"][field]
        exclude = filters["exclude"][field]

        # if include values were passed and its not a wildcard, check against it
        if "*" in include or getattr(obj, field) in include:
            included += 1
        # if include = * and the user is in the exclude list, reject
        if getattr(obj, field) in exclude:
            return False

        # otherwise include = * and there's no exclude, so continue checking

    if included == len(obj.supported_filters()):
        return True
    else:
        return False


def get_connection_key(database_name, username, pid):
    return f"{database_name}_{username}_{pid}"


def is_serverless(config):
    return bool(
        re.fullmatch(serverless_cluster_endpoint_pattern, config["target_cluster_endpoint"])
    )


def current_offset_ms(ref_time):
    return (datetime.datetime.now(tz=datetime.timezone.utc) - ref_time).total_seconds() * 1000.0


# exception thrown if credentials can't be retrieved
class CredentialsException(Exception):
    pass
