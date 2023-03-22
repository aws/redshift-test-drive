import base64
import datetime
import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("SimpleReplayLogger")


def redshift_describe_logging_status(source_cluster_endpoint):
    """
    Get the audit log location for the cluster via the API
    """
    logger.debug(f"Retrieving log location for {source_cluster_endpoint}")
    region = source_cluster_endpoint.split(".")[2]
    result = boto3.client("redshift", region).describe_logging_status(
        ClusterIdentifier=source_cluster_endpoint.split(".")[0]
    )
    return result


def redshift_get_cluster_credentials(
    region, user, database_name, cluster_id, duration=900, auto_create=False
):
    rs_client = boto3.client("redshift", region)
    try:
        response = rs_client.get_cluster_credentials(
            DbUser=user,
            DbName=database_name,
            ClusterIdentifier=cluster_id,
            DurationSeconds=duration,
            AutoCreate=auto_create,
        )
    except rs_client.exceptions.ClusterNotFoundFault:
        logger.error(
            f"Cluster {cluster_id} not found. Please confirm cluster endpoint, account, and region."
        )
        exit(-1)
    return response


def redshift_execute_query(
    redshift_cluster_id, redshift_user, redshift_database_name, region, query
):
    """
    Executes redshift query and gets response for query when finished
    """
    # get query id
    redshift_data_api_client = boto3.client("redshift-data", region)
    response_execute_statement = redshift_data_api_client.execute_statement(
        Database=redshift_database_name,
        DbUser=redshift_user,
        Sql=query,
        ClusterIdentifier=redshift_cluster_id,
    )
    query_id = response_execute_statement["Id"]

    # get query status
    response_describe_statement = redshift_data_api_client.describe_statement(
        Id=query_id
    )
    query_done = False

    while not query_done:
        response_describe_statement = redshift_data_api_client.describe_statement(
            Id=query_id
        )
        query_status = response_describe_statement["Status"]

        if query_status == "FAILED":
            logger.debug(f"SQL execution failed. Query ID = {query_id}")
            raise Exception

        elif query_status == "FINISHED":
            query_done = True
            # log result if there is a result (typically from Select statement)
            if response_describe_statement["HasResultSet"]:
                response_get_statement_result = (
                    redshift_data_api_client.get_statement_result(Id=query_id)
                )
    return response_get_statement_result


def cw_describe_log_groups(log_group_name=None, region=None):
    cloudwatch_client = boto3.client("logs", region)
    if log_group_name:
        return cloudwatch_client.describe_log_groups(logGroupNamePrefix=log_group_name)
    else:
        response_pg_1 = cloudwatch_client.describe_log_groups()
        logs = response_pg_1

        if 'nextToken' in response_pg_1.keys():
            token = response_pg_1['nextToken']
            while token != '':
                response_itr = cloudwatch_client.describe_log_groups(nextToken=token)
                logs['logGroups'].extend(response_itr['logGroups'])
                if 'nextToken' in response_itr.keys():
                    token = response_itr['nextToken']
                else:
                    token = ''
    return logs


def cw_describe_log_streams(log_group_name, region):
    cloudwatch_client = boto3.client("logs", region)
    return cloudwatch_client.describe_log_streams(logGroupName=log_group_name)


def cw_get_paginated_logs(
    log_group_name, log_stream_name, start_time, end_time, region
):
    log_list = []
    cloudwatch_client = boto3.client("logs", region)
    paginator = cloudwatch_client.get_paginator("filter_log_events")
    pagination_config = {"MaxItems": 10000}
    convert_to_millis_since_epoch = (
        lambda time: int(
            (
                time.replace(tzinfo=None) - datetime.datetime.utcfromtimestamp(0)
            ).total_seconds()
        )
        * 1000
    )
    start_time_millis_since_epoch = convert_to_millis_since_epoch(start_time)
    end_time_millis_since_epoch = convert_to_millis_since_epoch(end_time)
    response_iterator = paginator.paginate(
        logGroupName=log_group_name,
        logStreamNames=[log_stream_name],
        startTime=start_time_millis_since_epoch,
        endTime=end_time_millis_since_epoch,
        PaginationConfig=pagination_config,
    )
    next_token = None
    while next_token != "":
        for response in response_iterator:
            next_token = response.get("nextToken", "")
            for event in response["events"]:
                log_list.append(event["message"])
        pagination_config.update({"StartingToken": next_token})
        response_iterator = paginator.paginate(
            logGroupName=log_group_name,
            logStreamNames=[log_stream_name],
            startTime=start_time_millis_since_epoch,
            endTime=end_time_millis_since_epoch,
            PaginationConfig=pagination_config,
        )
    return log_list


def s3_upload(local_file_name, bucket, key=None):
    s3 = boto3.resource("s3")
    k = key if key else local_file_name
    s3.meta.client.upload_file(local_file_name, bucket, k)
    return s3.Object(bucket, k)


def s3_put_object(file_content, bucket, key):
    s3 = boto3.client("s3")
    s3.put_object(Body=file_content, Bucket=bucket, Key=key)

def s3_resource_put_object(bucket,prefix,body):
    s3_resource = boto3.resource("s3")
    s3_resource.Object(bucket,prefix).put(Body=body)

def s3_get_bucket_contents(bucket, prefix):
    conn = boto3.client("s3")

    # get first set of
    response = conn.list_objects_v2(Bucket=bucket, Prefix=prefix)
    bucket_objects = response.get("Contents", [])

    if "NextContinuationToken" in response:
        prev_key = response["NextContinuationToken"]
        while True:
            response = conn.list_objects_v2(
                Bucket=bucket, Prefix=prefix, ContinuationToken=prev_key
            )
            bucket_objects.extend(response["Contents"])
            if "NextContinuationToken" not in response:
                break
            prev_key = response["NextContinuationToken"]
    return bucket_objects


def s3_generate_presigned_url(client_method, bucket_name, object_name):
    s3_client = boto3.client("s3")
    response = s3_client.generate_presigned_url(
        client_method,
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=604800,
    )
    return response

def s3_copy_object(src_bucket, src_prefix, dest_bucket, dest_prefix):
    boto3.client("s3").copy_object(
        Bucket=dest_bucket,
        Key=dest_prefix,
        CopySource={"Bucket": src_bucket, "Key": src_prefix},
    )


def s3_get_object(bucket, filename):
    s3 = boto3.resource("s3")
    return s3.Object(bucket, filename)


def s3_client_get_object(bucket, key):
    s3 = boto3.client("s3")
    return s3.get_object(Bucket=bucket, Key=key)


def glue_get_table(database, table, region):
    table_get_response = boto3.client("glue", region).get_table(
        DatabaseName=database,
        Name=table,
    )
    return table_get_response


def glue_get_partition_indexes(database, table, region):
    index_response = boto3.client("glue", region).get_partition_indexes(
        DatabaseName=database,
        TableName=table,
    )
    return index_response


def glue_create_table(new_database, table_input, region):
    boto3.client("glue", region).create_table(
        DatabaseName=new_database, TableInput=table_input
    )


def glue_get_database(name, region):
    boto3.client("glue", region).get_database(Name=name)


def glue_create_database(name, description, region):
    boto3.client("glue", region).create_database(
        DatabaseInput={
            "Name": name,
            "Description": description,
        }
    )


def get_secret(secret_name, region_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = None

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        # secret_string = json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            # Use is not authorized to perform secretsmanager:GetSecretValue on requested resource
            raise e

    # Decrypts secret using the associated KMS key.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if "SecretString" in get_secret_value_response:
        secret = json.loads(get_secret_value_response["SecretString"])
    else:
        secret = json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))

    return secret
