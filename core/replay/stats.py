import logging

logger = logging.getLogger("WorkloadReplicatorLogger")


def percent(num, den):
    if den == 0:
        return 0
    return float(num) / den * 100.0


def print_stats(stats):
    if 0 not in stats:
        logger.warning("No stats gathered.")
        return

    max_connection_diff = 0
    for process_idx in stats.keys():
        if abs(stats[process_idx].get("connection_diff_sec", 0)) > abs(
            max_connection_diff
        ):
            max_connection_diff = stats[process_idx]["connection_diff_sec"]
        logger.debug(
            f"[{process_idx}] Max connection offset: {stats[process_idx].get('connection_diff_sec', 0):+.3f} sec"
        )
    logger.debug(f"Max connection offset: {max_connection_diff:+.3f} sec")


def display_stats(stats, total_queries, peak_connections):
    stats_str = ""
    stats_str += (
        f"Queries executed: {stats['query_success'] + stats['query_error']} of {total_queries} "
        f"({percent(stats['query_success'] + stats['query_error'], total_queries):.1f}%)"
    )
    stats_str += "  ["
    stats_str += f"Success: {stats['query_success']} ({percent(stats['query_success'], stats['query_success'] + stats['query_error']):.1f}%), "
    stats_str += f"Failed: {stats['query_error']} ({percent(stats['query_error'], stats['query_success'] + stats['query_error']):.1f}%), "
    stats_str += f"Peak connections: {peak_connections.value}"
    stats_str += "]"

    logger.info(f"{stats_str}")


def init_stats(stats_dict):
    # init by key to ensure Manager is notified of change, if applicable
    stats_dict["connection_diff_sec"] = 0
    stats_dict["transaction_success"] = 0
    stats_dict["transaction_error"] = 0
    stats_dict["query_success"] = 0
    stats_dict["query_error"] = 0
    stats_dict[
        "connection_error_log"
    ] = {}  # map filename to array of connection errors
    stats_dict[
        "transaction_error_log"
    ] = {}  # map filename to array of transaction errors
    stats_dict["multi_statements"] = 0
    stats_dict["executed_queries"] = 0  # includes multi-statement queries
    return stats_dict


def collect_stats(aggregated_stats, stats):
    """Aggregate the per-thread stats into the overall stats for this aggregated process"""

    if not stats:
        return

    # take the maximum absolute connection difference between actual and expected
    if abs(stats["connection_diff_sec"]) >= abs(
        aggregated_stats.get("connection_diff_sec", 0)
    ):
        aggregated_stats["connection_diff_sec"] = stats["connection_diff_sec"]

    # for each aggregated, add up these scalars across all threads
    for stat in (
        "transaction_success",
        "transaction_error",
        "query_success",
        "query_error",
    ):
        aggregated_stats[stat] += stats[stat]

    # same for arrays.
    for stat in ("transaction_error_log", "connection_error_log"):
        # note that per the Manager python docs, this extra copy is required to
        # get manager to notice the update
        new_stats = aggregated_stats[stat]
        new_stats.update(stats[stat])
        aggregated_stats[stat] = new_stats
