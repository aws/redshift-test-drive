# Behaviour checks for the redshift-test-drive skill

`test_skill_contract.py` checks that the skill names keys, targets and paths that exist. It
cannot check that an agent following the skill does the right thing. These prompts can: a
maintainer gives each one to an agent that has the skill loaded and checks the answer against
the expectations. A response fails if it misses an expectation or does anything in its
"must not" line.

Run them when an instruction in `SKILL.md` or a reference changes behaviour, and record the
result (date, agent, commit, pass/fail per item) at the end of this file.

## E1. Provisioned source readiness

**Prompt:** "I want to extract a workload from my provisioned Redshift cluster for Test Drive. What do I need to check first?"

**Expect:** `aws redshift describe-logging-status`; `enable_user_activity_logging` set to `true`
in the parameter group (with a reboot); audit logging covering the connection, user and user
activity logs; a snapshot taken before the window. **Must not:** tell the user to export logs
with `create-export-task`.

## E1b. Serverless source readiness

**Prompt:** "My source is Redshift Serverless. How do I get its audit logs ready for extraction?"

**Expect:** the namespace log exports include `useractivitylog` and `connectionlog`; the
extractor reads them from CloudWatch directly when the endpoint is a Serverless endpoint.
**Must not:** add an export-to-S3 step or point `source_cluster_system_table_unload_location`
at exported logs.

## E2. Replay configuration without COPY or UNLOAD

**Prompt:** "Configure the replay for my target cluster; I do not want any COPY or UNLOAD to run."

**Expect:** edit the shipped `config/replay.yaml`; `workload_location` is the full
`Extraction_<cluster>_<timestamp>` path; `execute_copy_statements` and
`execute_unload_statements` stay `"false"`; `analysis_iam_role` and `analysis_output` both set
for the report; the telemetry prefix on `make replay`. **Must not:** write a new YAML file or
invent keys such as `copy_replacements:`.

## E3. Early stop

**Prompt:** "My replay started five minutes ago and almost every statement in the worker log says relation does not exist. What now?"

**Expect:** stop the replay; check the database each connection uses (`connections.json`), the
schemas and `search_path` on the target, and grants; then replay again from the start.
**Must not:** let the replay run on, or edit `connections.json`.

## E4. Pre-flight

**Prompt:** "Before I start a four-hour replay, how do I make sure the target is ready?"

**Expect:** the five checks: users exist (or will run as `master_username`), tables exist and
have rows, nothing is loading, a workload user can run a query, the setting under test is live;
plus resolving the endpoint to a cluster or workgroup id and confirming it with the user.
**Must not:** offer a script of its own to run them.

## E5. Manual vs Auto WLM

**Prompt:** "I want to compare Manual WLM and Auto WLM for my workload with Test Drive."

**Expect:** two restores from one snapshot; a custom parameter group with
`wlm_json_configuration` set, attached and rebooted; everything else identical (including
concurrency scaling via `max_concurrency_scaling_clusters`); replay the baseline then the target
with different `tag` values. **Must not:** modify a default parameter group or suggest Manual
WLM on Serverless.

## E6. Datashare consumer replay

**Prompt:** "My consumer reads through a datashare and replayed statements fail with relation does not exist. How do I set the target up?"

**Expect:** sessions run in the database recorded in `connections.json`; recreate the datashare
database (same name) after the producer grants the share to the target namespace; recreate the
local external schema and `search_path` if the workload used them; endpoint database is a local
one such as `dev`; check whether the share grants writes before replaying. **Must not:** run
`DROP SCHEMA` (including `public ... CASCADE`) or replace the `public` schema.

## E7. Cache warming with COPY and UNLOAD

**Prompt:** "After a patch I want to pre-warm a cluster with my workload, including COPY and UNLOAD."

**Expect:** a cluster that is not live production; a warning that the replay re-runs the
window's writes (only S3 COPY and UNLOAD are held back) and consent for that; COPY needs `execute_copy_statements: "true"`
and the IAM-role column of `copy_replacements.csv` (only filled when `log_location` was set at
extract); UNLOAD needs `execute_unload_statements: "true"`, `unload_iam_role` and an S3
`replay_output`; the warm-up takes as long as the window. **Must not:** promise that warming a
copy speeds up production, call the warm-up read-only, say the flags hold back COPY/UNLOAD
inside stored procedures, or say Serverless has no compile time.

## E8. Reporting a result

**Prompt:** "My target replay shows 15% of matched statements more than 20% slower than the baseline. Should I adopt the target configuration?"

**Expect:** an assessment, not a bare verdict: both configurations, the window, success counts
per run, the matched count, two or three headline numbers with units, what differed outside the
variable, the tool's limits, and checks the user may want next. **Must not:** answer with a bare
"Adopt" or "Do not adopt".

## E9. RA3 to RG comparison

**Prompt:** "I have a 4-node ra3.4xlarge cluster. How do I use Test Drive to evaluate moving to RG?"

**Expect:** restore the target with the RG node type and the same node count; record both
configurations, including per-node vCPU, memory and slices from AWS documentation; one variable
only; a warm-up run before measuring. **Must not:** quote speed-up or price multipliers as
expected results.

## End-to-end runs

One maintainer, one agent, following only the skill through all eight steps, once per target
type. Required before the first release that ships the skill. Record the `application_name`
seen in `SYS_CONNECTION_LOG` on each target; it is the first check that the telemetry prefix
arrives.

| Target type | Date | Maintainer | Agent | Commit or tag | Baseline and target configuration | Replay ids | `application_name` seen | Outcome |
|---|---|---|---|---|---|---|---|---|
| Provisioned | | | | | | | | |
| Serverless | | | | | | | | |

## Results

| Date | Agent | Commit | E1 | E1b | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
