import csv
import threading
import common.aws_service as aws_helper
import logging

from tqdm import tqdm
from common.util import bucket_dict


logger = logging.getLogger("SimpleReplayLogger")


def copy_parallel(dest_bucket, dest_prefix, source_location, obj_type):
    threads = [None] * len(source_location)
    pbar = tqdm(range(len(source_location)))
    for i in pbar:
        threads[i] = threading.Thread(
            target=aws_helper.s3_copy_object,
            args=(
                source_location[i]["source_bucket"],
                source_location[i]["source_key"],
                dest_bucket,
                (f"{dest_prefix}{source_location[i]['source_key']}"),
            ),
        )
        threads[i].start()
        pbar.set_description(
            f"Cloning {source_location[i]['source_key']} - {i + 1} out of {len(source_location)} {obj_type}"
        )

    for i in range(len(source_location)):
        threads[i].join()


def get_s3_folder_size(copy_file_list):
    """
    This function will calculate size of every folder inside the copy_replacement.csv
    @param copy_file_list:
    @return:
    """
    total_size = 0
    for record in copy_file_list:
        prefix = record["source_key"]
        if not prefix.endswith("/"):
            total_size = total_size + record["bytes"]
    return size_of_data(total_size)


def check_file_existence(response, obj_type):
    source_location = []
    objects_not_found = []
    for record in response["Records"]:
        if obj_type == "copyfiles":
            source_url = bucket_dict(record[0]["stringValue"])
            source_bucket = source_url["bucket_name"]
            source_key = (source_url["prefix"])[:-1]
        else:
            source_bucket = record[0]["stringValue"]
            source_key = record[1]["stringValue"][:-1]
        objects = aws_helper.s3_get_bucket_contents(source_bucket, source_key)
        if not objects:  # if no object is found, add it to objects_not_found list
            objects_not_found.append({"source_bucket": source_bucket, "source_key": source_key})
        else:  # if object is found, append it to source_location to be cloned
            for object in objects:
                source_location.append(
                    {
                        "source_bucket": source_bucket,
                        "source_key": object["Key"],
                        "e_tag": object["ETag"],
                        "size": size_of_data(object["Size"]),
                        "bytes": object["Size"],
                        "last_modified": object["LastModified"],
                    }
                )
    return source_location, objects_not_found


def clone_objects_to_s3(target_dest, obj_type, source_location, objects_not_found):
    dest_location = bucket_dict(target_dest)
    dest_prefix = f"{dest_location['prefix']}{obj_type}/"
    dest_bucket = dest_location["bucket_name"]
    if obj_type == "copyfiles":
        file_output = "Final_Copy_Objects.csv"
        full_object_type = "COPY command files"
    else:
        file_output = "Spectrum_objects_copy_report.csv"
        full_object_type = "Spectrum files"
    copy_parallel(
        dest_bucket=dest_bucket,
        dest_prefix=dest_prefix,
        source_location=source_location,
        obj_type=full_object_type,
    )
    logger.info(
        f"{len(source_location)} {full_object_type} cloned to s3://{dest_bucket}/{dest_prefix}"
    )

    with open(file_output, "w") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "Source Location",
                "Destination Location",
                "Size",
                "Etag",
                "Last Modified Date",
            ],
        )
        writer.writeheader()

        if source_location:
            fp.write(f"Cloned below objects: \n")
            for obj in source_location:
                fp.write(
                    f"s3://{obj['source_bucket']}/{obj['source_key']},"
                    f"s3://{dest_bucket}{dest_prefix}{obj['source_key']},{obj['size']},{obj['e_tag']},"
                    f"{obj['last_modified']}\n"
                )
            fp.write(f"Number of objects cloned: {len(source_location)}\n")
        if objects_not_found:
            fp.write(f"Failed to clone below objects: \n")
            for obj in objects_not_found:
                fp.write(
                    f"s3://{obj['source_bucket']}/{obj['source_key']},Object not found,N/A,N/A,N/A\n"
                )
            fp.write(f"Number of objects not found: {len(objects_not_found)}")
    aws_helper.s3_upload(file_output, bucket=f"{dest_bucket}", key=f"{dest_prefix}{file_output}")
    logger.info(
        f"Details of {full_object_type} cloning uploaded to {dest_bucket}/{dest_prefix}{file_output}"
    )
    logger.info(f"== Finished cloning {full_object_type} ==")


def size_of_data(size_in_bytes):
    """
    Categorise bytes in GB,MB,TB
    @param size_in_bytes:
    @return:
    """
    float_size_in_bytes = float(size_in_bytes)
    kilobytes = float(1024)
    megabytes = float(kilobytes**2)  # 1,048,576
    gigabytes = float(kilobytes**3)  # 1,073,741,824
    terabytes = float(kilobytes**4)  # 1,099,511,627,776

    if float_size_in_bytes < kilobytes:
        return "{0} {1}".format(
            float_size_in_bytes, "B" if 0 == float_size_in_bytes > 1 else "Byte"
        )
    elif kilobytes <= float_size_in_bytes < megabytes:
        return "{0:.2f} KB".format(float_size_in_bytes / kilobytes)
    elif megabytes <= float_size_in_bytes < gigabytes:
        return "{0:.2f} MB".format(float_size_in_bytes / megabytes)
    elif gigabytes <= float_size_in_bytes < terabytes:
        return "{0:.2f} GB".format(float_size_in_bytes / gigabytes)
    elif terabytes <= float_size_in_bytes:
        return "{0:.2f} TB".format(float_size_in_bytes / terabytes)