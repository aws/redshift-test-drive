---
name: redshift-test-drive
description: "Runs Amazon Redshift Test Drive from this repository to measure how a real workload behaves on a different Redshift configuration before the change is made: extracts the workload from audit logs (Workload Replicator), replays it on a baseline and a target (Auto vs Manual WLM, node type or count change such as RA3 to RG, provisioned to Serverless, RPU size, a new patch, a datashare consumer size) and reads the results with Replay Analysis or NodeConfigCompare. Use when the user asks about the performance impact of a Redshift configuration change on their own queries, wants to validate a change before a resize or migration, wants to pre-warm a cluster after a patch, or has Test Drive output to interpret or troubleshoot (stalled replay, connection limit, schema does not exist, external schemas). Does not apply to general Redshift SQL, query tuning, WLM or resize questions without a workload replay, to Teradata or other migrations, or to a change the user will make without measuring."
license: Apache-2.0
compatibility: "Needs a shell on a host (normally an EC2 instance in the Redshift VPC) with git, make, Python 3.10–3.12, the AWS CLI with credentials, and network access to the source and target Redshift endpoints. The skill runs the code in this repository; it ships no code of its own."
metadata:
  version: "1"
  telemetry-channel: "skill/1"
  owner: "aws/redshift-test-drive maintainers"
---

# Redshift Test Drive: agent skill

This skill drives the tools in this repository. It never writes a configuration file from
memory: you edit the shipped `config/extract.yaml` and `config/replay.yaml`, run the `make`
targets in the root `Makefile`, and read the outputs the tools produce. The skill, the code and
the READMEs are versioned together; the release tag you
cloned is the version of all three.

If something here disagrees with `core/README.md` or the code, the code wins; report the
discrepancy as a GitHub issue.

## When to use / when not to

Use this skill when the user wants evidence about *their own workload* on a different Redshift
configuration, or needs help running or interpreting a Test Drive they already started.

Do not use it to answer general Redshift questions, to tune individual queries, or to perform a
resize, WLM change or migration the user has already decided on. Test Drive measures; it does not
migrate.

## Which tool for which journey

| Journey | Tool | Read first |
|---|---|---|
| Replay one extracted workload on one or two targets you set up yourself | Workload Replicator (`make extract`, `make replay`) | `core/README.md` |
| Compare several configurations (node types, RPU sizes, WLM variants, datashare consumer sizes) with the clusters and workgroups created for you (provisioned clusters are paused afterwards when `AUTO_PAUSE` is true; you delete the clusters, workgroups and namespaces yourself) | NodeConfigCompare (CloudFormation + Step Functions + AWS Batch) | `tools/NodeConfigCompare/README.md` |
| Look at replay results: throughput, percentiles, latency distribution, top queries, errors, COPY metrics, across selected replays | Replay Analysis (`make replay_analysis`, web UI on port 3000) | `tools/ReplayAnalysis/README.md` |
| The workload reads Spectrum external tables or COPYs from S3 that the target cannot reach | External Object Replicator (`make external_object_replicator`), provisioned sources only | `tools/ExternalObjectReplicator/README.md` |

Default to the Workload Replicator for a two-way comparison the user controls; propose
NodeConfigCompare when there are three or more candidate configurations or the user prefers a
fully automated run.

## Before anything runs: prerequisites and consent

Confirm each item with the user and record the answers; stop if any is missing.
Details and the exact checks are in [prerequisites-and-consent](references/prerequisites-and-consent.md).

1. Audit logging is on for the source: connection log, user log and user activity log, with
   `enable_user_activity_logging = true` (provisioned) or `useractivitylog` and `connectionlog`
   in the namespace log exports (Serverless). The upstream README warns that S3 delivery can
   take around three hours (`core/README.md`); AWS documents no fixed delivery time.
2. The replay target is **not production**. It is a snapshot restore (or a new workgroup) the
   user is willing to change and delete.
3. COPY and UNLOAD stay **off** (`execute_copy_statements: "false"`,
   `execute_unload_statements: "false"`, the shipped defaults) unless the user explicitly asks
   for them and supplies the replacement S3 locations and IAM role. COPY/UNLOAD inside stored
   procedures run regardless.
4. The user accepts the cost: target cluster or workgroup hours, the EC2 host, S3 storage, and
   that a replay takes about as long as the original window (the replayer holds every statement
   to its original offset).
5. The user accepts that `SQLs.json.gz` and `connections.json` contain production SQL text and
   user names, and names the S3 bucket where they may live.
6. Which run is the **baseline** and which is the **target**. Never infer it from folder names.

## Telemetry (MUST)

Every `make extract` and `make replay` you start MUST carry the skill channel so maintainers can
see that a run was agent-driven. Prefix the command in the same shell invocation; do not rely on
an earlier `export` surviving between tool calls:

```bash
cd "$REDSHIFT_TEST_DRIVE_ROOT" && REDSHIFT_TEST_DRIVE_CLIENT=skill/1 make extract
cd "$REDSHIFT_TEST_DRIVE_ROOT" && REDSHIFT_TEST_DRIVE_CLIENT=skill/1 make replay
```

The tool sets the connection parameter `application_name` to
`RedshiftTestDrive-<Component>/<git-sha7>/skill/1` (see the Telemetry section of `README.md`);
on code older than the first release tag the variable is ignored. It carries no workload data.
The value after `skill/` must equal `metadata.version` in this file (the contract test in
`skills/tests/` enforces it).

## The core journey

Work through the steps in order. Each step names the file or target it uses.

### 1. Frame the comparison

- One variable at a time: same snapshot, same data, same workload window; only the configuration
  under test differs between baseline and target.
- Record both configurations now (node type and count from
  `aws redshift describe-clusters`, or base RPU from `aws redshift-serverless get-workgroup`).
  They go next to every number you report.
- Pick a window of 1–4 hours that contains the peak the user cares about; longer windows replay
  for as long as the original.

### 2. Prepare the host

Follow `README.md` "Preparations" and `core/README.md` Step 2 on an EC2 instance in the
clusters' VPC (recommended `m5.8xlarge`, 32 GB SSD). Clone at the newest release tag so the
version in the telemetry marker is a tagged commit:

```bash
git clone --depth 1 --branch "<latest vYYYY.MM.DD-sha7 tag>" https://github.com/aws/redshift-test-drive.git
cd redshift-test-drive && export REDSHIFT_TEST_DRIVE_ROOT=$(pwd)
python3 -m venv testDriveEnv && source testDriveEnv/bin/activate && make setup
```

If no tag exists yet, clone `main` and record `git rev-parse --short HEAD`. Run long steps
inside `tmux`, `screen` or an SSM Session Manager session with `nohup`, so a dropped SSH session
does not kill the replay. Logs are under `core/logs/` in the repository root (step 6).

### 3. Extract

Edit `config/extract.yaml` (do not create a new file; every key the validator reads is already
there). Set `workload_location`, `source_cluster_endpoint` (`<name>.<id>.<region>.redshift.amazonaws.com:<port>/<db>`),
`master_username`, `region`, `start_time`/`end_time` (ISO 8601 with offset, quoted). Decide
`external_schemas`: listing a schema **removes** its statements from the workload into
`sql_statements_skipped.txt`; leave it empty to replay them (and then make the external tables
reachable from the target, see step 4). Serverless sources are read from CloudWatch directly;
there is no export step. Then run the extract (telemetry prefix as above).

Output lands in `<workload_location>/Extraction_<cluster>_<timestamp>/` as `SQLs.json.gz`,
`connections.json`, `copy_replacements.csv` and, when statements were skipped,
`sql_statements_skipped.txt`. Open `sql_statements_skipped.txt` and the row count of
`copy_replacements.csv` with the user before going on.
Procedure and checks: [run-extract-and-replay](references/run-extract-and-replay.md).

### 4. Set up baseline and target

Restore the target from the source snapshot (`core/README.md`, Replay, "Preparation") and apply
exactly the change under test: parameter group with `auto_wlm`, `resize-cluster` or
`restore-from-cluster-snapshot` with another node type, a workgroup with another `--base-capacity`,
a different maintenance track. For a datashare consumer target see
[datashare-consumer](references/datashare-consumer.md). Commands, warm-up guidance and the
equal-compute rule: [target-setup](references/target-setup.md).

### 5. Pre-flight the target

Before a multi-hour replay, from the `Extraction_*` folder: the users in `connections.json`
exist on the target (or the user accepts that IAM identities will run as `master_username`), the
tables the workload touches exist and have rows, nothing is loading, a sample query runs as a
workload user, and the WLM or RPU setting on the target is the one under test. Checklist with
SQL: [run-extract-and-replay](references/run-extract-and-replay.md#pre-flight).

### 6. Replay: baseline first, then target

Edit `config/replay.yaml`:

- `workload_location`: the full `.../Extraction_<cluster>_<timestamp>` path (not its parent).
- `target_cluster_endpoint`, `target_cluster_region`, `master_username`.
- `tag`: a label such as `baseline-manualwlm` or `target-autowlm`; it becomes part of the replay id.
- `analysis_iam_role` **and** `analysis_output`: both are needed for the analysis CSVs and PDF.
- Leave `execute_copy_statements`/`execute_unload_statements` at `"false"` unless consented
  (COPY then needs the third column of `copy_replacements.csv`, UNLOAD needs `unload_iam_role`
  and an S3 `replay_output`).
- `time_interval_between_transactions`/`_queries`: leave at `""`. Pacing is fixed: every
  statement keeps its original offset whatever these say (see
  [run-extract-and-replay](references/run-extract-and-replay.md)).
- `limit_concurrent_connections` when the target has a session limit; `num_workers` for the host.
- Serverless target: `secret_name` is optional. Without it the tool calls `GetClusterCredentials`
  for each workload user (`AutoCreate` off, so the user must exist on the target), with
  `master_username` substituted for `IAM:`/`IAMR:`/two-colon names, using the identifier
  `redshift-serverless-<workgroup>`; with it, every user runs as the secret's admin.

Immediately before `make replay`, resolve the endpoint in `replay.yaml` to a cluster or workgroup
id and ARN with `describe-clusters`/`get-workgroup`, show it to the user, and get a yes. Start the
replay detached with the telemetry prefix. In the first minutes tail the worker logs under
`core/logs/replay_log-<replay_id>/` (per-statement errors) and the main log under
`core/logs/replay/`; if most statements fail, stop and go to
[troubleshooting](references/troubleshooting.md). Repeat for the target with a different `tag`.

### 7. Read the results

Each replay with analysis enabled writes, under `analysis_output`, `analysis/<replay_id>/raw_data/`
(CSV-format UNLOAD files without an extension, for example `sys_query_history000` and
`query_metrics000`; the replayer adds `replayerrors000` there when statements failed),
`aggregated_data/*.csv`, and `out/info.json` plus `out/<replay_id>_report.pdf`. Compare runs in
Replay Analysis (`make replay_analysis`) or load the CSVs.
Match the same statement across runs by the watermark the replayer prepends to every statement
(`/* {"xid": ..., "query_idx": ..., "replay_start": ..., "source": "Test-Drive"} */`), never by `query_id`.
In `raw_data/sys_query_history000` the `elapsed_time`, `queue_time` and `execution_time` columns
are microseconds; `query_metrics000` and the `aggregated_data` CSVs convert them to seconds
(`*_s` columns). A statement that succeeded on the baseline and failed on the target is a
regression, not a speed-up. Method and caveats:
[results-and-interpretation](references/results-and-interpretation.md).

### 8. Report, then clean up

Report with the template in [results-and-interpretation](references/results-and-interpretation.md#assessment-template):
both configurations, the window, the success rates, the matched-statement count, 2–3 headline
numbers, what differed outside the variable under test, and what the tool cannot show. Then run
the [cleanup](references/cleanup.md) checklist: final snapshot, delete target and host, remove the
run's S3 prefix, restore any parameter group you changed.

## Safety checkpoints

- Never replay against production. Confirm the resolved target identity right before every replay.
- Baseline-vs-target is the user's statement, recorded before analysis.
- A replay runs every extracted statement, including writes and DDL; only statements that read
  from or write to S3 are held back. The non-production target is the safeguard, not the
  COPY/UNLOAD flags.
- COPY and UNLOAD off unless the user enables them and supplies replacement locations.
- Stop a replay whose first minutes are mostly failures; fix permissions, do not let it run on.
- Prefer `limit_concurrent_connections` over editing `connections.json`; do not edit `SQLs.json.gz`.
- Production metrics are not a baseline. Replay the same workload on a baseline restore.
- A target with less compute than the baseline is expected to regress; say so before running.
- Always run detached and with the telemetry prefix.

## Troubleshooting routes

| Symptom | Go to |
|---|---|
| Replay stalls, holds locks, or finishes far faster or slower than the window | [troubleshooting](references/troubleshooting.md#pacing) |
| `connection limit exceeded` / `too many connections for user` | [troubleshooting](references/troubleshooting.md#connections) |
| `relation does not exist`, `schema does not exist`, `permission denied for schema` | [troubleshooting](references/troubleshooting.md#schema) |
| Spectrum or external-table statements missing from the replay | [troubleshooting](references/troubleshooting.md#external-schemas) |
| `copy_replacements.csv` is empty or COPY statements are skipped | [troubleshooting](references/troubleshooting.md#copy) |
| NodeConfigCompare Step Functions or AWS Batch failure | [troubleshooting](references/troubleshooting.md#nodeconfigcompare) and `tools/NodeConfigCompare/README.md` "Troubleshooting" |
| Lost the SSH session; is the replay still running? | [troubleshooting](references/troubleshooting.md#detached) |
| Two replays of the same extract differ in query count or timings | [results-and-interpretation](references/results-and-interpretation.md#variance) |

## What the tool does not do (say so to the user)

- Federated identities: `IAM:`/`IAMR:` and two-colon user names are replayed as `master_username`;
  on a Serverless target with `secret_name`, all users run as the secret's admin (the key is
  ignored for provisioned targets). So WLM rules keyed on those users' groups or roles are not
  exercised (queue assignment follows the connecting user; `SET query_group` in the replayed SQL
  still applies).
- Spectrum statements run only if the target can reach the external tables; otherwise list the
  schemas in `external_schemas` so they are skipped visibly.
- COPY/UNLOAD inside stored procedures are neither redirected nor held back: a replayed `CALL`
  runs them against their original S3 locations unless the procedure is altered or removed
  first (`core/README.md` "Limitations").
- JDBC-specific behaviour, bind-parameter procedures and cross-connection ordering are not
  reproduced (`core/README.md` "Limitations").
- The tool's own reports do not break out compile time on either platform, and the
  `stl_compile_info` UNLOAD is shipped commented out in `core/replay/unload_system_tables.sql`.
  When compile time matters, query `sys_query_history.compile_time` on the target yourself
  (see [results-and-interpretation](references/results-and-interpretation.md)).
- The tools report measurements; they do not choose a configuration. Neither should you without
  stating the evidence and its limits.
- Test Drive is open-source software, not an AWS service feature; AWS documentation links to it
  but describes no support coverage. Questions and defects go to the repository's issue tracker
  (`CONTRIBUTING.md`), not to an AWS Support case.

## References

| File | What it holds |
|---|---|
| [prerequisites-and-consent](references/prerequisites-and-consent.md) | Audit-log and permission checks, consent record, cost and data-handling notes |
| [run-extract-and-replay](references/run-extract-and-replay.md) | Key-by-key guidance for the shipped `config/extract.yaml` and `config/replay.yaml`, pre-flight checklist, target binding, outputs |
| [target-setup](references/target-setup.md) | Snapshot restore, resize, parameter group / Auto WLM, RPU, maintenance track, equal-compute rule, warm-up run |
| [datashare-consumer](references/datashare-consumer.md) | Replaying on a datashare consumer: external schema + `search_path`, grants, NodeConfigCompare datashare mode |
| [troubleshooting](references/troubleshooting.md) | The failure patterns users actually hit, with the config key or log to look at |
| [results-and-interpretation](references/results-and-interpretation.md) | Output layout, watermark matching, units, variance, assessment template |
| [patch-validation-and-cache-warming](references/patch-validation-and-cache-warming.md) | Using a replay to validate a patch or pre-warm compilation cache |
| [cleanup](references/cleanup.md) | Verify-before-delete checklist for clusters, workgroups, host, S3 prefix, parameter groups |
