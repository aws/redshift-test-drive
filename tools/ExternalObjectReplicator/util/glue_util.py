import logging
import uuid

from moto.glue.exceptions import DatabaseNotFoundException, TableNotFoundException

import common.aws_service as aws_helper

from tqdm import tqdm
from common.util import bucket_dict

logger = logging.getLogger("SimpleReplayLogger")


def clone_glue_catalog(records, dest_location, region):
    """
    It reads through the systems table to create clone of the database,tables and partitions
    record[3]['stringValue'] : glue database vale from table
    record[2]['stringValue'] : external glue table value
    @param records:
    @param region
    @param dest_location
    @return:
    """
    glue_db_append_name = uuid.uuid1()
    new_glue_db_list = []
    checked_db_list = []
    pbar = tqdm(range(len(records)))
    for i in pbar:
        record = records[i]
        original_glue_db = record[3]["stringValue"]
        original_glue_table = record[2]["stringValue"]
        new_glue_db = f"{glue_db_append_name}-{original_glue_db}"
        pbar.set_description_str(
            f"Cloning {original_glue_table} in {original_glue_db} - {i + 1} out of {len(records)} glue objects"
        )
        # if the database hasn't been checked yet
        if original_glue_db not in checked_db_list:
            database_copy(new_glue_db, original_glue_db, original_glue_table, region)
            checked_db_list.append(original_glue_db)
            new_glue_db_list.append(new_glue_db)
        glue_table_copy(original_glue_db, new_glue_db, original_glue_table, dest_location, region)
    logger.debug(f"New Glue database created: {new_glue_db_list}.")
    logger.info("== Finished cloning Glue databases and tables ==")
    return new_glue_db_list


def database_copy(new_glue_db, original_glue_db, original_glue_table, region):
    """
    Create a new database
    @return:

    Parameters
    ----------
    region
    original_glue_table
    original_glue_db
    new_glue_db
    """
    try:
        aws_helper.glue_get_database(name=new_glue_db, region=region)
    except DatabaseNotFoundException as _:
        aws_helper.glue_create_database(
            new_glue_db, "Database clone created by External Object Replicator", region
        )
    except Exception as e:
        logger.error(f"Error doing database copy in Glue: {e}")
        exit(-1)

    return original_glue_db, new_glue_db, original_glue_table


def glue_table_copy(original_glue_db, new_glue_db, original_glue_table, dest_location, region):
    """
    CHeck if glue table exists in the new glue database, if not create the table structure along with the partitions
    @param original_glue_db:
    @param new_glue_db:
    @param original_glue_table:
    @param dest_location
    @param region
    @return:
    """
    dest_bucket = bucket_dict(dest_location)["bucket_name"]
    try:
        table_get_response = aws_helper.glue_get_table(
            database=new_glue_db, table=original_glue_table, region=region
        )
        new_s3_loc = table_get_response["Table"]["StorageDescriptor"]["Location"]
    except TableNotFoundException as _:
        table_get_response = aws_helper.glue_get_table(
            database=original_glue_db,
            table=original_glue_table,
            region=region,
        )
        index_response = aws_helper.glue_get_partition_indexes(
            database=original_glue_db, table=original_glue_table, region=region
        )
        orig_s3_loc = table_get_response["Table"]["StorageDescriptor"]["Location"].split("/")
        new_s3_loc = f"{dest_bucket}/spectrumfiles/{'/'.join(orig_s3_loc[2:])}"
        table_input = (
            {
                "Name": table_get_response["Table"]["Name"],
                "Description": "For use with Redshfit candidate release testing",
                "StorageDescriptor": {
                    "Columns": table_get_response["Table"]["StorageDescriptor"]["Columns"],
                    "Location": new_s3_loc,
                },
                "PartitionKeys": table_get_response["Table"]["PartitionKeys"],
            },
        )
        if index_response["PartitionIndexDescriptorList"]:
            aws_helper.glue_create_table(
                new_database=new_glue_db,
                table_input=table_input.update(
                    {'PartitionIndexes"': index_response["PartitionIndexDescriptorList"]}
                ),
                region=region,
            )
        else:
            aws_helper.glue_create_table(
                new_database=new_glue_db, table_input=table_input[0], region=region
            )
        return new_s3_loc
    except Exception as e:
        logger.error(f"Failed to copy table in Glue: {e}")
        exit(-1)
