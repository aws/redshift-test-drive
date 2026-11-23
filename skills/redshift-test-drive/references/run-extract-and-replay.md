# Run extract and replay

## Contents

- [Extract: keys to set](#extract-keys-to-set)
- [Extract: run and check the output](#extract-run-and-check-the-output)
- [Replay: keys to set](#replay-keys-to-set)
- [Pre-flight](#pre-flight)
- [Bind the replay to its target](#bind-the-replay-to-its-target)
- [Replay: run and watch](#replay-run-and-watch)
- [Outputs](#outputs)

Edit the shipped files. Do not write a new `config/extract.yaml` or `config/replay.yaml`:
the validator in `common/config.py` reads keys the shipped files already contain and exits
when one is missing. Leave keys you do not need at their shipped values.

## Extract: keys to set

Keys of `config/extract.yaml`:

| Key | Set to |
|---|---|
| `workload_location` | S3 prefix (or local directory) the user named for the workload files |
| `source_cluster_endpoint` | `<name>.<id>.<region>.redshift.amazonaws.com:<port>/<db>`, or the workgroup endpoint for Serverless |
| `master_username` | An admin user on the source; required when the endpoint is set |
| `region` | The source region; required when the endpoint is set |
| `start_time` | Window start, ISO 8601 with offset, quoted, for example `"2026-06-14T09:00:00+00:00"` |
| `end_time` | Window end, same format |
| `log_location` | Leave empty to let the extractor locate the audit logs. Set it when COPY statements must be replayed, because `copy_replacements.csv` is only filled when this key is set: the S3 audit-log location for a provisioned source, the CloudWatch log group for a Serverless source |
| `replacement_copy_location`, `replacement_iam_location` | Optional: S3 location and IAM role written into every row of `copy_replacements.csv`, so its "Replacement IAM role" column does not have to be filled by hand |
| `external_schemas` | See the next paragraph |
| `source_cluster_system_table_unload_location` | Optional S3 output location for the source's system tables (provisioned) |
| `source_cluster_system_table_unload_iam_role` | IAM role for that UNLOAD; leave both empty to skip it |

`external_schemas`: every statement that references a listed schema (`schema.table`, any case)
is **removed** from the workload and written to `sql_statements_skipped.txt`. Leave it empty
to replay those statements, and then make the external tables reachable from the target
(`tools/ExternalObjectReplicator/README.md`, provisioned sources only). List a schema only when
the user accepts that its statements will not run.

## Extract: run and check the output

```bash
cd "$REDSHIFT_TEST_DRIVE_ROOT" && REDSHIFT_TEST_DRIVE_CLIENT=skill/1 make extract
```

Output: `<workload_location>/Extraction_<cluster>_<timestamp>/` (`Extraction_<timestamp>` when
no endpoint is set) containing `SQLs.json.gz`,
`connections.json`, `copy_replacements.csv` and, when statements were removed,
`sql_statements_skipped.txt`. The extract log is under `core/logs/extract/`. Before going on,
show the user the number of connections and statements in the log, the contents of
`sql_statements_skipped.txt`, and the number of rows in `copy_replacements.csv` (a header-only
file means COPY cannot be replayed from this extract).

Never edit `SQLs.json.gz` or `connections.json`.

## Replay: keys to set

Keys of `config/replay.yaml`:

| Key | Set to |
|---|---|
| `workload_location` | The full `.../Extraction_<cluster>_<timestamp>` path, not its parent |
| `target_cluster_endpoint` | Endpoint of the restore under test, with `:<port>/<db>` |
| `target_cluster_region` | Region of the target |
| `master_username` | Admin user on the target |
| `tag` | A label such as `baseline-autowlm`; it becomes part of the replay id |
| `analysis_iam_role` | Role the target uses to UNLOAD the analysis data; needed with the next key |
| `analysis_output` | S3 location for the analysis CSVs and PDF; also receives `replayerrors000` |
| `replay_output` | S3 location for system-table UNLOADs and replayed UNLOADs (optional) |
| `execute_copy_statements` | `"false"` unless consented; `"true"` also needs the IAM-role column of `copy_replacements.csv` filled |
| `execute_unload_statements` | `"false"` unless consented; `"true"` also needs `unload_iam_role` and an S3 `replay_output` |
| `unload_iam_role` | Required when `execute_unload_statements` is `"true"`: without it the UNLOAD is sent unredirected and fails on the `IAM_ROLE ''` the extractor blanked in, or, if the original used `IAM_ROLE default`, writes to its original location. `"false"` is what keeps UNLOADs out |
| `target_cluster_system_table_unload_iam_role` | IAM role for the target's system-table UNLOAD into `replay_output` (provisioned targets); empty skips it |
| `nlb_nat_dns` | Serverless only, optional: an NLB or NAT DNS name to connect through when the host is outside the workgroup's VPC |
| `time_interval_between_transactions` | Leave `""` (see below) |
| `time_interval_between_queries` | Leave `""` |
| `limit_concurrent_connections` | A cap when the target has a session limit |
| `num_workers` | Processes on the host; empty means the CPU count minus one, at least 4 |
| `secret_name` | Serverless only, optional: every user then runs as the secret's admin; the secret must hold `admin_username` and `admin_password` |
| `filters` | Optional include/exclude lists by `database_name`, `username`, `pid` |

Pacing: every statement waits for its original offset from the workload start, whatever the two
`time_interval_between_*` keys say, so a replay lasts about as long as the window. `"all off"`
only removes the extra wait between a connection's transactions and its wait to disconnect;
`""` behaves the same, because the extractor writes `null` for the per-connection flags. Connections start at their original offsets in every mode.

Serverless without `secret_name`: the tool requests temporary credentials for each workload user
(the user must already exist on the target) and substitutes `master_username` for `IAM:`,
`IAMR:` and two-colon names.

## Pre-flight

Run these read-only checks on the target before a long replay; stop on the first failure.

1. **Users.** Every `username` in `connections.json` exists on the target, except the `IAM:`,
   `IAMR:` and two-colon names that will run as `master_username`:
   `SELECT usename FROM pg_user ORDER BY 1;`
2. **Tables have data.** As a superuser (or a user granted SELECT on `SVV_TABLE_INFO`),
   connected to each database the workload uses:
   `SELECT "schema", "table", tbl_rows FROM svv_table_info WHERE "schema" IN ('<schema>') ORDER BY 1, 2;`
   `SVV_TABLE_INFO` lists only tables with at least one row, so a table the workload reads that
   is missing from the output is empty or absent, and the restore is wrong.
3. **Nothing is loading.**
   `SELECT query_id, query_type, status, start_time FROM sys_query_history WHERE status IN ('running','queued') ORDER BY start_time;`
4. **A workload user can run a query.** As a superuser:
   `SET SESSION AUTHORIZATION '<user>'; SELECT COUNT(*) FROM <schema>.<table>; SET SESSION AUTHORIZATION DEFAULT;`
5. **The setting under test is live.** Provisioned:
   `aws redshift describe-clusters --cluster-identifier <target> --query 'Clusters[0].{Node:NodeType,Nodes:NumberOfNodes,PG:ClusterParameterGroups}'`
   (the parameter group must show `in-sync`). Serverless:
   `aws redshift-serverless get-workgroup --workgroup-name <wg> --query 'workgroup.baseCapacity'`.

## Bind the replay to its target

Immediately before each `make replay`, read `target_cluster_endpoint` from `config/replay.yaml`,
resolve it with `aws redshift describe-clusters` (match `Endpoint.Address`) or
`aws redshift-serverless get-workgroup`, and show the user the account, region, cluster or
workgroup id and ARN. Replay only after an explicit yes. If the id differs from the target you
pre-flighted, pre-flight again.

## Replay: run and watch

Run detached so a dropped SSH session does not stop it:

```bash
cd "$REDSHIFT_TEST_DRIVE_ROOT" && REDSHIFT_TEST_DRIVE_CLIENT=skill/1 nohup make replay > replay-<tag>.out 2>&1 &
```

In the first minutes, read the per-worker logs in `core/logs/replay_log-<replay_id>/` (per-statement
errors) and the main log in `core/logs/replay/`. If most statements fail, stop the replay and go
to [troubleshooting](troubleshooting.md). Replay the baseline first, then the target with another
`tag`; never run both against the same restore at once.

## Outputs

- `replay_id` is `<start time>_<cluster id>_<tag>_<hash>`.
- `analysis_output`: `analysis/<replay_id>/` with `raw_data/`, `aggregated_data/` and `out/`
  (see [results-and-interpretation](results-and-interpretation.md)).
- `replay_output`: `<replay_id>/system_tables/<TABLE>/` when
  `target_cluster_system_table_unload_iam_role` is set (provisioned targets only), plus any
  replayed UNLOAD output.
- In the repository root where `make` ran: `extract_logs.zip`, `replay_logs.zip`,
  `replay_worker_logs.zip`, `info.json` and the `<replay_id>_report.pdf`. When
  `workload_location` is in S3 the log zips are also uploaded there under fixed names, so each
  replay overwrites the previous one: copy the baseline's logs off before the target replay.
