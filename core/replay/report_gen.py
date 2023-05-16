import datetime
import os
import pandas as pd
import yaml
import boto3
import json
import logging
import re
import redshift_connector

from boto3 import client
from botocore.exceptions import ClientError
from contextlib import contextmanager
from tabulate import tabulate
from io import StringIO
from pandas import CategoricalDtype
from functools import partial
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    TableStyle,
    Table,
    Spacer,
    Image,
    SimpleDocTemplate,
    Paragraph,
    ListFlowable,
    ListItem,
)

import common.aws_service
from core.replay.report_util import (
    styles,
    build_pdf_tables,
    df_to_np,
    first_page,
    later_pages,
    hist_gen,
    sub_yaml_vars,
)
from common import util
from common import aws_service as aws_service_helper
import core.replay.report_util as report_util

g_stylesheet = styles()
g_columns = g_stylesheet.get("columns")


def pdf_gen(report, summary=None):
    """This function formats the summary report using the content from report_content.yaml to populate the paragraphs,
       titles, and headers. The tables are populated via the Report param which has all the dataframes.

    @param report: Report object
    @param summary: list, replay summary

    """
    with open("core/replay/report_content.yaml", "r") as stream:
        docs = yaml.safe_load(stream)

        style = g_stylesheet.get("styles")
        elems = []  # elements array used to build pdf structure
        pdf = SimpleDocTemplate(
            f"{report.replay_id}_report.pdf",
            pagesize=letter,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # title and subtitle and cluster info table
        elems.append(Paragraph(docs["title"], style["Title"]))
        elems.append(Paragraph(sub_yaml_vars(report, docs["subtitle"]), style["Heading4"]))
        cluster_info = pd.DataFrame.from_dict(report.cluster_details, orient="index")
        elems.append(
            Table(
                df_to_np(report.cluster_details.keys(), cluster_info.transpose()),
                hAlign="LEFT",
                style=g_stylesheet.get("table_style"),
            )
        )
        # replay summary
        if summary is not None:
            elems.append(Paragraph(f"Replay Summary", style["Heading4"]))
            elems.append(
                ListFlowable(
                    [ListItem(Paragraph(x, style["Normal"])) for x in summary],
                    bulletType="bullet",
                )
            )
            elems.append(Spacer(0, 5))

        elems.append(Paragraph(docs["report_paragraph"], style["Normal"]))

        # glossary section
        elems.append(Paragraph(docs["glossary_header"], style["Heading4"]))
        elems.append(Paragraph(docs["glossary_paragraph"], style["Normal"]))
        elems.append(
            ListFlowable(
                [ListItem(Paragraph(x, style["Normal"])) for x in docs["glossary"]],
                bulletType="bullet",
            )
        )
        elems.append(Spacer(0, 5))

        # access data section
        elems.append(Paragraph(docs["data_header"], style["Heading4"]))
        elems.append(Paragraph(sub_yaml_vars(report, docs["data_paragraph"]), style["Normal"]))
        elems.append(
            ListFlowable(
                [ListItem(Paragraph(x, style["Normal"])) for x in docs["raw_data"]],
                bulletType="bullet",
            )
        )
        elems.append(Spacer(0, 5))
        elems.append(Paragraph(sub_yaml_vars(report, docs["agg_data_paragraph"]), style["Normal"]))

        # notes section
        elems.append(Paragraph(docs["notes_header"], style["Heading4"]))
        elems.append(Paragraph(docs["notes_paragraph"], style["Normal"]))
        elems.append(
            ListFlowable(
                [ListItem(Paragraph(x, style["Normal"])) for x in docs["notes"]],
                bulletType="bullet",
            )
        )

        elems.append(PageBreak())  # page 2: cluster details

        # query breakdown
        build_pdf_tables(elems, docs["query_breakdown"], report)
        elems.append(Spacer(0, 5))

        # histogram and description
        image_path = hist_gen(
            x_data=report.feature_graph["sec_start"],
            y_data=report.feature_graph["count"],
            title=docs["graph"].get("title"),
            x_label="Average Elapsed Time (s)",
        )

        desc = Paragraph(docs["graph"].get("paragraph"), style["Normal"])
        data = [[Image(image_path, width=300, height=200, hAlign="LEFT"), desc]]
        elems.append(Table(data, style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")])))
        elems.append(Spacer(0, 5))

        # cluster metrics table
        build_pdf_tables(elems, docs["cluster_metrics"], report)

        elems.append(PageBreak())  # page 3+ measure tables

        build_pdf_tables(
            elems, docs["measure_tables"], report
        )  # build 5 measure tables all at once

        # build pdf
        pdf.build(
            elems,
            onFirstPage=partial(first_page, report=report),
            onLaterPages=partial(later_pages, report=report),
        )
        os.remove(image_path)

        return pdf.filename


def replay_pdf_generator(
    replay,
    cluster_endpoint,
    start_time,
    end_time,
    bucket_url,
    iam_role,
    user,
    tag="",
    workload="",
    is_serverless=False,
    secret_name=None,
    nlb_nat_dns=None,
    complete=True,
    stats=None,
    summary=None,
):
    """End to end data collection, parsing, analysis and pdf generation

    @param replay: str, replay id from replay.py
    @param cluster_endpoint: str, target cluster endpoint
    @param start_time: datetime object, start time of replay
    @param end_time: datetime object, end time of replay
    @param bucket_url: str, S3 bucket location
    @param iam_role: str, IAM ARN for unload
    @param user: str, master username for cluster
    @param tag: str, optional identifier
    @param is_serverless: bool, serverless or provisioned cluster
    @param secret_name: str, name of the secret that stores admin username and password
    @param nlb_nat_dns: str, dns endpoint if specified will be used to connect instead of target cluster endpoint
    @param complete: bool, complete/incomplete replay run
    @param stats: dict, run details
    @param summary: str list, replay output summary from replay.py
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")
    s3_client = boto3.client("s3")
    cluster = util.cluster_dict(cluster_endpoint, is_serverless, start_time, end_time)
    cluster["is_serverless"] = is_serverless
    cluster["secret_name"] = secret_name
    cluster["host"] = nlb_nat_dns if nlb_nat_dns != None else cluster["host"]

    if type(bucket_url) is str:
        bucket = util.bucket_dict(bucket_url)

    logger.debug(bucket)

    logger.info(f"Running analysis for replay: {replay}")
    replay_path = f"{bucket['prefix']}analysis/{replay}"

    # unload from cluster
    queries = unload(bucket, iam_role, cluster, user, replay)
    info = create_json(replay, cluster, workload, complete, stats, tag)
    try:
        aws_service_helper.s3_upload(info, bucket.get("bucket_name"), f"{replay_path}/{info}")
    except ClientError as e:
        logger.error(f"{e} Could not upload info. Confirm IAM permissions include S3::PutObject.")
        exit(-1)

    report = report_util.Report(cluster, replay, bucket, replay_path, tag, complete)

    try:
        # iterate through query csv results and import
        for q in queries:
            get_raw_data(report, bucket, replay_path, q)

    except Exception as e:
        logger.error(f"{e}: Data read failed. Error in replay analysis.")
        exit(-1)

    logger.info(f'Pdf generation is completed and the data uploaded at {bucket.get("bucket_name")}/{replay_path} and can be used in Replay Analysis.')

    # generate replay_id_report.pdf and info.json
    logger.info(f"Generating report.")
    pdf = pdf_gen(report, summary)

    # upload to s3 and output presigned urls
    try:
        aws_service_helper.s3_upload(pdf, bucket.get("bucket_name"), f"{replay_path}/out/{pdf}")
        aws_service_helper.s3_upload(info, bucket.get("bucket_name"), f"{replay_path}/out/{info}")
        analysis_summary(bucket.get("url"), replay)
        
    except ClientError as e:
        logger.error(
            f"{e} Could not upload report. Confirm IAM permissions include S3::PutObject."
        )
        exit(-1)


@contextmanager
def initiate_connection(username, cluster):
    """Initiate connection with Redshift cluster

    @param username: master username from replay.yaml
    @param cluster: cluster dictionary
    """

    response = None
    logger = logging.getLogger("WorkloadReplicatorLogger")
    secret_keys = ["admin_username", "admin_password"]

    if cluster.get("is_serverless"):
        if cluster.get("secret_name"):
            logger.info(f"Fetching secrets from: {cluster.get['secret_name']}")
            secret_name = common.aws_service.get_secret(
                cluster.get("secret_name"), cluster.get("region")
            )
            if not len(set(secret_keys) - set(secret_name.keys())):
                response = {
                    "DbUser": secret_name["admin_username"],
                    "DbPassword": secret_name["admin_password"],
                }
            else:
                logger.error(f"Required secrets not found: {secret_keys}")
                exit(-1)
        else:
            serverless_cluster_id = f"redshift-serverless-{cluster.get('id')}"
            logger.debug(
                f"Serverless cluster id {serverless_cluster_id} passed to get_cluster_credentials"
            )
            response = aws_service_helper.redshift_get_cluster_credentials(
                cluster.get("region"), username, cluster.get("database"), serverless_cluster_id
            )

    else:
        try:
            response = aws_service_helper.redshift_get_cluster_credentials(
                cluster.get("region"), username, cluster.get("database"), cluster.get("id")
            )
        except Exception as e:
            logger.error(
                f"Unable to connect to Redshift. Confirm IAM permissions include Redshift::GetClusterCredentials."
                f" {e}"
            )
            exit(-1)

    if response is None or response.get("DbPassword") is None:
        logger.error(f"Failed to retrieve credentials for user {username} ")
        response = None
        exit(-1)

    # define cluster string/dict
    cluster_string = {
        "username": response["DbUser"],
        "password": response["DbPassword"],
        "host": cluster.get("host"),
        "port": cluster.get("port"),
        "database": cluster.get("database"),
    }

    conn = None
    try:
        logger.info(f"Connecting to {cluster.get('id')}")
        conn = util.db_connect(
            host=cluster_string["host"],
            port=int(cluster_string["port"]),
            username=cluster_string["username"],
            password=cluster_string["password"],
            database=cluster_string["database"],
        )  # yield to reuse connection
        yield conn
    except Exception as e:
        logger.error(f"Unable to connect to Redshift. {e}", exc_info=True)
        exit(-1)
    finally:
        if conn is not None:
            conn.close()


# def unload(unload_location, iam_role, cluster, user, path):
def unload(unload_location, iam_role, cluster, user, replay):
    """Iterates through sql/ and executes UNLOAD with queries on provided cluster

    @param unload_location: S3 bucket location for unloaded data
    @param iam_role: IAM ARN with unload permissions
    @param cluster: cluster dict
    @param user: str, master username for cluster
    @param path: replay path
    @return: str List, query file names
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")

    directory = r"core/sql"

    queries = []  # used to return query names
    with initiate_connection(username=user, cluster=cluster) as conn:  # initiate connection
        cursor = conn.cursor()
        logger.info(f"Querying {cluster.get('id')}. This may take some time.")

        for file in sorted(os.listdir(directory)):  # iterate local sql/ directory
            if not file.endswith(".sql"):  # validity check
                continue
            with open(f"{directory}/{file}", "r") as query_file:  # open sql file
                # get file name prefix for s3 files
                query_name = os.path.splitext(file)[0]  # get file/query name for reference
                logger.debug(f"Query: {query_name}")
                queries.append(query_name)
                query = query_file.read()  # read file contents as string

                # replace start and end times in sql with variables
                query = re.sub(r"{{START_TIME}}", f"'{cluster.get('start_time')}'", query)
                query = re.sub(r"{{END_TIME}}", f"'{cluster.get('end_time')}'", query)

                # format unload query with actual query from sql/
                unload_query = (
                    f"unload ($${query}$$) to '{unload_location.get('url')}/analysis/{replay}/raw_data/"
                    f"{query_name}' iam_role '{iam_role}' CSV header allowoverwrite parallel off;"
                )
                try:
                    cursor.execute(unload_query)  # execute unload
                except Exception as e:
                    logger.error(
                        f"Could not unload {query_name} results. Confirm IAM permissions include UNLOAD "
                        f"access for Redshift. {e}"
                    )
                    exit(-1)

    logger.info(f"Query results available in {unload_location.get('url')}")
    return queries


def get_raw_data(report, bucket, replay_path, query):
    """Reads and processes raw data from S3

    @param report: Report, report object
    @param bucket: dict, S3 bucket location
    @param replay_path: str, path of replay
    @param query: str, query name
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")
    try:
        response = aws_service_helper.s3_client_get_object(
            bucket=bucket.get("bucket_name"), key=f"{replay_path}/raw_data/{query}000"
        )
    except Exception as e:
        logger.error(f"Unable to get raw data from S3. Results for {query} not found. {e}")
        exit(-1)
    df = pd.read_csv(response.get("Body")).fillna(0)
    logger.debug(f"Parsing results from '{query}' query.")
    if query == "latency_distribution":
        report.feature_graph = df
    else:
        for t, vals in report.tables.items():
            if vals.get("sql") == query:
                vals["data"] = read_data(t, df, vals.get("columns"), report)


def read_data(table_name, df, report_columns, report):
    """Map raw data file to formatted table

    @param table_name: name of table
    @param df: DataFrame of raw data
    @param report_columns: List of column names for report table
    @param report: Report object
    @return: DataFrame of formatted data
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")

    if df.empty:
        logger.error("Data is empty. Failed to generate report.")
        exit(-1)
    cols = [g_columns[x] for x in report_columns]
    table_type = report.tables.get(table_name).get("type")

    report_table = None
    if table_type == "breakdown":
        report_table = df[cols]
    elif table_type == "metric":
        order = CategoricalDtype(
            [
                "Query Latency",
                "Compile Time",
                "Queue Time",
                "Execution Time",
                "Commit Queue Time",
                "Commit Time",
            ],
            ordered=True,
        )
        df[g_columns.get("Measure")] = df[g_columns.get("Measure")].astype(order)
        frame = df.sort_values(g_columns.get("Measure"))
        report_table = frame[cols]
    elif table_type == "measure":  # filter for specific measure type
        report_table = df[cols][df[g_columns.get("Measure")] == table_name]

    report_table = pd.DataFrame(report_table).round(
        2
    )  # round values in dataframe to thousandths place
    report_table.reindex(columns=report_columns)  # add columns names to dataframe

    # upload formatted dataframe to S3 as csv
    try:
        file = f"{table_name.replace(' ', '')}.csv"  # set filename for saving
        csv_buffer = StringIO()
        report_table.to_csv(csv_buffer)
        logger.debug(report.bucket)
        aws_service_helper.s3_resource_put_object(
            report.bucket.get("bucket_name"),
            f"{report.path}/aggregated_data/{file}",
            csv_buffer.getvalue(),
        )
    except Exception as e:
        logger.error(
            f"Could not upload aggregated data. Please confirm bucket. Error occurred while processing "
            f"data. {e}"
        )
        exit(-1)
    return report_table


def create_presigned_url(bucket_name, object_name):
    """Creates a presigned url for a given object

    @param bucket_name: str, bucket name
    @param object_name: str, object name
    @return:
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")

    try:
        response = aws_service_helper.s3_generate_presigned_url(
            client_method="get_object", bucket_name=bucket_name, object_name=object_name
        )
    except ClientError as e:
        logger.error(
            f"Unable to generate presigned url for object {object_name} in bucket {bucket_name}. {e}"
        )
        return None

    return response


def analysis_summary(bucket_url, replay):
    """Print presigned url for report of given replay

    @param bucket_url: str, S3 bucket location
    @param replay: str, replay id
    """

    logger = logging.getLogger("WorkloadReplicatorLogger")

    bucket = util.bucket_dict(bucket_url)
    logger.info(f"Simple Replay Workload Analysis: {replay}")
    replay_path = f"analysis/{replay}/out/"
    output_str = (
        f"\nBelow is the presigned URLs for the analysis performed for replay: {replay}. "
        f"Click or copy/paste the link into your browser to download."
    )
    r_url = create_presigned_url(bucket.get("bucket_name"), f"{replay_path}{replay}_report.pdf")
    output_str += f"\n\nReplay Analysis Report | Click to Download:\n{r_url}\n"
    logger.info(output_str)


def create_json(replay, cluster, workload, complete, stats, tag=""):
    """Generates a JSON containing cluster details for the replay"""

    if cluster["start_time"] and cluster["end_time"]:
        duration = cluster["end_time"] - cluster["start_time"]
        duration = duration - datetime.timedelta(microseconds=duration.microseconds)

        cluster["start_time"] = str(cluster["start_time"].isoformat(timespec="seconds"))
        cluster["end_time"] = str(cluster["end_time"].isoformat(timespec="seconds"))
        cluster["duration"] = str(duration)

    if complete:
        cluster["status"] = "Complete"
    else:
        cluster["status"] = "Incomplete"

    cluster["replay_id"] = replay
    cluster["replay_tag"] = tag
    cluster["workload"] = workload

    if stats:
        for k, v in enumerate(stats):
            cluster[v] = stats[v]

    # cluster["connection_success"] = cluster["connection_count"] - cluster["connection_errors"]

    json_object = json.dumps(cluster, indent=4)
    with open(f"info.json", "w") as outfile:
        outfile.write(json_object)
        return outfile.name
