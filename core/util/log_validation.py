"""
log_validation..py
====================================
This module validates the logs parsed by auditlogs_parsing.py
"""

import dateutil.parser
import datetime
import re


def is_valid_log(log, start_time, end_time):
    """If query doesn't contain problem statements, saves it."""
    problem_keywords = [
        "INTERNAL QUERY */",
        "DEALLOCATE pdo_stmt_",
        "UNLISTEN *",
        "context: SQL",
        "ERROR:",
        "CONTEXT:  SQL",
        "show ",
        "Undoing transaction",
        "Undo on",
        "pg_terminate_backend",
        "pg_cancel_backend",
        "volt_",
        "pg_temp_",
    ]

    potential_problem_keywords = ["BIND"]

    not_problem_keywords = ["BINDING"]

    if log.username == "rdsdb":
        return False

    if start_time and log.record_time < start_time:
        return False

    if end_time and log.record_time > end_time:
        return False

    if any(word in log.text for word in problem_keywords):
        return False

    if any(word in log.text for word in potential_problem_keywords) and not any(
        word in log.text for word in not_problem_keywords
    ):
        return False

    # filter internal statement rewrites with parameter markers
    if re.search("\$\d", log.text):
        # remove \$\d in string literals ( select '$1' ) or comment blocks ( */ $1 */ )
        text_without_valid_parameter_markers = re.sub(
            """'.*\\$\\d.*'|\\/\\*.*\\$\\d.*\\*\\/""", "", log.text, flags=re.DOTALL
        )
        # remove \$\d in single line quotes ( -- $1 )
        if "--" in log.text:
            text_without_valid_parameter_markers = re.sub(
                "^\s*--.*\$\d", "", text_without_valid_parameter_markers
            )
        # if there are still parameter markers remaining after removing them from valid cases, the query text is invalid
        if re.search("\$\d", text_without_valid_parameter_markers):
            return False

    return True


def is_duplicate(first_query_text, second_query_text):
    dedupe_these = [
        "set",
        "select",
        "create",
        "delete",
        "update",
        "insert",
        "copy",
        "unload",
        "with",
    ]

    first_query_text = first_query_text.strip()
    second_query_text = second_query_text.strip()
    first_query_text_no_semi = first_query_text.replace(";", "")
    second_query_tex_no_semi = second_query_text.replace(";", "")
    second_query_comment_removed = second_query_text
    first_query_comment_removed = first_query_text
    if second_query_text.startswith("/*"):
        second_query_comment_removed = second_query_text[
            second_query_text.find("*/") + 2 : len(second_query_text)
        ].strip()
    if first_query_text.startswith("/*"):
        first_query_comment_removed = first_query_text[
            second_query_text.find("*/") + 2 : len(first_query_text)
        ].strip()
    return (
        (
            first_query_text_no_semi == second_query_tex_no_semi
            and any(second_query_comment_removed.startswith(word) for word in dedupe_these)
        )
        or (
            (second_query_comment_removed.lower().startswith("create"))
            and (first_query_comment_removed.lower().startswith("create"))
            and second_query_comment_removed.endswith(";")
        )
        or (
            (second_query_comment_removed.lower().startswith("drop"))
            and (first_query_comment_removed.lower().startswith("drop"))
            and second_query_comment_removed.endswith(";")
        )
        or (
            (second_query_comment_removed.lower().startswith("alter"))
            and (first_query_comment_removed.lower().startswith("alter"))
            and second_query_comment_removed.endswith(";")
        )
    )


def get_logs_in_range(audit_objects, start_time, end_time):
    start_idx = None
    end_idx = None
    filenames = []
    for index, log in list(enumerate(audit_objects)):
        filename = log["Key"].split("/")[-1]
        file_datetime = dateutil.parser.parse(filename.split("_")[-1][:-3].replace("_", ":")).replace(
            tzinfo=datetime.timezone.utc
        )
        if start_time and file_datetime < start_time:
            continue

        if end_time and file_datetime > end_time:
            # make sure we've started
            if len(filenames) > 0:
                filenames.append(log["Key"])
            break

        # start with one before the first file to make sure we capture everything
        if len(filenames) == 0 and index > 0:
            filenames.append(audit_objects[index - 1]["Key"])

        filenames.append(log["Key"])

    return filenames


def remove_line_comments(query):
    removed_string = query
    prev_location = 0

    while True:
        line_comment_begin = removed_string.find("--", prev_location)
        prev_location = line_comment_begin

        # no more comments to find
        if line_comment_begin == -1:
            break

        # found_comment = True
        linebreak = removed_string.find("\n", line_comment_begin)
        start_comment = removed_string.find(
            "/*",
            line_comment_begin,
            linebreak if linebreak != -1 else len(removed_string),
        )
        end_comment = removed_string.find(
            "*/",
            line_comment_begin,
            linebreak if linebreak != -1 else len(removed_string),
        )

        if linebreak != -1:
            if start_comment == -1 and end_comment != -1:
                # if line comment is between start and end, then remove until end of comment
                removed_string = removed_string[:line_comment_begin] + removed_string[end_comment:]
            else:
                # else remove up the end of line
                removed_string = removed_string[:line_comment_begin] + removed_string[linebreak:]
        else:
            # reached end of query
            if start_comment == -1 and end_comment != -1:
                # if line comment is between start and end, then remove until end of comment

                removed_string = removed_string[:line_comment_begin] + removed_string[end_comment:]
            else:
                # else remove up the end of line
                removed_string = removed_string[:line_comment_begin]

    return removed_string
