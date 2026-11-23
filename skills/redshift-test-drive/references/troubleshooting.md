# Troubleshooting

## Contents

- [Early stop](#early-stop)
- [Pacing](#pacing)
- [Connections](#connections)
- [Schema](#schema)
- [External schemas](#external-schemas)
- [COPY](#copy)
- [NodeConfigCompare](#nodeconfigcompare)
- [Detached](#detached)

Per-statement errors are in the worker logs under `core/logs/replay_log-<replay_id>/`; the main
replay log is under `core/logs/replay/` and the extract log under `core/logs/extract/`. Read the
log before changing anything, and change one thing at a time.

## Early stop

If most statements fail in the first minutes of a replay, stop it rather than let it run for
the whole window: Ctrl-C in the foreground, or `pkill -INT -f replay.py` for a detached run (the
replayer handles SIGINT only). Fix the cause on the target,
then replay again from the start with the same `tag`. If the stopped run had already executed
writes, restore the target again from the snapshot first so it starts from the same data as the
baseline. Common first-minute causes, by message:

| Message in the worker log | Usual cause |
|---|---|
| `relation ... does not exist` | Wrong database or schema on the target; see [Schema](#schema) |
| `permission denied for schema` / `for relation` | Grants missing on the restore |
| `Permission denied to query database created from datashare` | Missing `GRANT USAGE ON DATABASE`; see [datashare-consumer](datashare-consumer.md) |
| `Error while getting cluster credentials` / `password authentication failed` | Host role lacks `redshift:GetClusterCredentials`, or the user does not exist on the target |
| `connection refused` / timeout | Host cannot reach the endpoint: security group, VPC, port |

## Pacing

At this version the replayer holds every statement to its original offset from the start of the
workload, whatever `time_interval_between_transactions` and `time_interval_between_queries` are
set to. `"all off"` only removes the extra wait between a connection's transactions and its wait
to disconnect. Consequences to explain to the user:

- A replay lasts about as long as the extracted window. It cannot be compressed by
  configuration; shorten the window at extract time instead.
- When the target is slower, statements start late and queue behind each other, so the replay
  runs longer than the window and later statements see more contention than in production.
  That is a result, not a tool fault.
- A replay that seems to stall is usually waiting for the next statement's offset in a quiet
  part of the window. The worker log's debug lines show how long each statement waits.
- Locks held by long transactions on the target block later statements just as in production.
  If a replay holds locks far longer than the baseline, compare the same transactions in both
  runs before blaming the tool.

Do not edit `connections.json` or `SQLs.json.gz` to change the pacing; the comparison is only
fair when baseline and target replay the identical files.

## Connections

`connection limit exceeded` or `too many connections for user` means the target refused new
sessions. Check, in this order:

1. The target's own connection quota and any user-level `CONNECTION LIMIT` set with
   `CREATE USER` or `ALTER USER`. A restore keeps the source's user settings.
2. Set `limit_concurrent_connections` in `config/replay.yaml` to a value under the limit. The
   replayer then holds new connections until a slot frees; record the value, because it changes
   concurrency compared with production.
3. `num_workers` controls host processes, not database sessions; raise it only if the host is the
   bottleneck.

Warnings that a connection started more than `connection_tolerance_sec` from its expected time
mean the host or the cap is delaying sessions.

## Schema

`schema does not exist`, `relation does not exist` or `permission denied for schema` on a
restore that should have everything:

- The session runs in the database recorded in `connections.json`. Check that database exists
  on the target with the same name; the endpoint's database does not change it.
- The restore was taken from a snapshot older than objects the workload creates or uses, or the
  objects are created by statements outside the extracted window. Extract a window that includes
  their creation, or create them on both restores before replaying.
- The user's `search_path` differs from the source. Compare `SHOW search_path` as that user on
  the source and the target.
- On a datashare consumer, the datashare database or the local external schema is missing; see
  [datashare-consumer](datashare-consumer.md).

## External schemas

Spectrum or other external-table statements missing from the replay:

- If `external_schemas` lists the schema, the extractor removed those statements and wrote them
  to `sql_statements_skipped.txt`. That is by design.
- If it does not, the statements were replayed and failed because the target cannot reach the
  external tables. Make them reachable (same external schema, catalog and IAM role on the
  target), or copy the objects with the External Object Replicator
  (`make external_object_replicator`, `tools/ExternalObjectReplicator/README.md`; provisioned
  sources only), or list the schema in `external_schemas` and re-extract so the gap is visible.

## COPY

`copy_replacements.csv` is empty, or COPY statements are skipped:

- The file is only filled when `log_location` is set in `config/extract.yaml`. An extract that
  used only `source_cluster_endpoint` produces a header-only file. Re-extract with
  `log_location` set to the S3 audit-log location.
- Replaying COPY needs `execute_copy_statements: "true"` and a role in the third column
  ("Replacement IAM role") of every row; the second column can redirect the source location.
- COPY or UNLOAD inside stored procedures is neither redirected nor held back: a replayed
  `CALL` runs it against the original S3 location. Alter or remove the procedure first
  (`core/README.md` "Limitations").

## NodeConfigCompare

Failures are in the Step Functions execution and the AWS Batch jobs. Follow
`tools/NodeConfigCompare/README.md` "Troubleshooting": with the default public image,
`CannotPullContainerError` usually means the subnet has no route to the internet to pull it;
with a private ECR image it can also point to ECR/S3 VPC endpoint, DNS, security-group, IAM or
image-reference configuration. Other failures are in the
CloudWatch log group `<stack name>/log` and in the failed step's CloudWatch Logs. After a fix,
start a new execution of the state machine.

## Detached

If the SSH session dropped, the replay survives only if it was started with `nohup`, `tmux`,
`screen` or an SSM Session Manager session. Reconnect and check:

```bash
pgrep -af "replay.py" ; ls -t "$REDSHIFT_TEST_DRIVE_ROOT"/core/logs/replay/ | head -3
```

If no process is running and the main log stopped early, the replay died with the session.
Start it again detached, with the same `tag` and the telemetry prefix.
