# Results and interpretation

## Contents

- [Name the runs](#name-the-runs)
- [Output layout](#output-layout)
- [Units and what the numbers include](#units-and-what-the-numbers-include)
- [Success first](#success-first)
- [Matching the same statement across runs](#matching-the-same-statement-across-runs)
- [Variance](#variance)
- [Cost](#cost)
- [Assessment template](#assessment-template)

## Name the runs

Baseline and target are whatever the user said in the consent record. Do not infer them from
`tag` values, S3 paths or timestamps. With several targets, compare each against the one
baseline; do not compare targets only with each other.

## Output layout

For each replay with `analysis_iam_role` and `analysis_output` set, under
`<analysis_output>/analysis/<replay_id>/`:

- `raw_data/`: CSV-format UNLOAD output without a file extension, one file per analysis query,
  for example `sys_query_history000` and `query_metrics000`. When statements failed, the
  replayer also writes `replayerrors000` here.
- `aggregated_data/`: the CSVs behind the report tables.
- `out/info.json` (cluster id, run start and end, duration, `replay_tag`, status) and
  `out/<replay_id>_report.pdf`.

Replay Analysis (`make replay_analysis`, `tools/ReplayAnalysis/README.md`) reads these for
selected replays and compares them in a browser: throughput, percentiles, latency
distribution, top queries, errors and COPY metrics.

## Units and what the numbers include

- In `raw_data/sys_query_history000`, `elapsed_time`, `queue_time` and `execution_time` are
  **microseconds** (as in `SYS_QUERY_HISTORY`). `query_metrics000` and the `aggregated_data` CSVs
  convert to seconds (`*_s` columns).
- The tool's analysis reads `sys_query_history` elapsed, queue and execution time only. Its
  execution time includes compilation; it does not break compile time out on either platform.
  When compile time matters, query `sys_query_history.compile_time` on the target directly while
  it still exists (it is available on provisioned and Serverless). `core/README.md` "Limitations
  specific to Serverless" states the missing compile metric for Serverless only.
- `query_metrics000` excludes failed statements, so its averages describe the statements that
  succeeded. Compare success rates separately.
- The `sys_query_history000` export covers everything in the replay window, including the tool's
  own connections. Keep only rows whose `query_text` carries the replay watermark.
- System tables are not in snapshots: per-query deep dives (`sys_query_detail` on both platforms,
  STL/SVL views on provisioned only) need the target to still exist.

## Success first

Before any timing: count attempted, succeeded and failed statements for each run
(`replayerrors000`, the report's error section, the main replay log summary, and the
`connection_errors/` and `transaction_errors/` files under `<workload_location>/<replay_id>/`).
COPY and UNLOAD statements the replayer held back are counted as successes in the summary, so
subtract them before comparing success rates. A statement that
succeeded on the baseline and failed on the target is a regression, never a speed-up; leave it
out of every timing comparison and report it on its own. If the failure counts differ a lot,
fix the cause and replay again before comparing times.

## Matching the same statement across runs

The replayer prepends a watermark to every statement it sends:

```text
/* {"xid": "<original xid>", "query_idx": <n>, "replay_start": "<iso time>", "source": "Test-Drive"} */ <statement>
```

`xid` is the transaction id from the original workload and `query_idx` the statement's position
in it, so the pair identifies the same statement in every replay of the same extract. Never
match on `query_id`, which is assigned by each target.

With `split_multi: true` (the default), each sub-statement of a multi-statement query is sent
separately with the **same** `xid` and `query_idx`. Count those rows; do not de-duplicate them.
When matching, pair them by their order within the same `xid` and `query_idx`.

## Variance

Two replays of the same extract on the same configuration are never identical. Causes to check
before attributing a difference to the configuration: cache warmth (first replay on a restore),
automatic maintenance on the target during the run, concurrency scaling, statements that failed
in one run only, and connections delayed by `limit_concurrent_connections` or the host. When the
decision depends on a small difference, replay each configuration twice and compare medians and
p90 across both pairs.

## Cost

Use current prices from the AWS pricing page for the user's region; do not use a remembered rate.

- Serverless: sum `charged_seconds` from `SYS_SERVERLESS_USAGE` over the replay window on the
  target, divide by 3600 for RPU-hours, multiply by the regional RPU-hour price. The view keeps
  seven days and is visible only to superusers, so read it soon after the replay.
- Provisioned: node count × hours × the node type's price (on-demand or the user's reserved rate).

A replay compresses nothing, so its cost is roughly one window's cost, not a month's. Say how
any projection was made.

## Assessment template

The tools measure; they do not choose. Deliver an assessment, not a verdict:

1. **Configurations:** baseline and target, as recorded (node type and count or base RPU,
   parameter group, maintenance track).
2. **Window:** start and end of the extract; replay start and end for each run.
3. **Coverage:** statements attempted and succeeded per run; matched statements used for the
   comparison; statements in `sql_statements_skipped.txt`.
4. **Headline numbers:** two or three, each with its unit and both values (for example median
   and p90 elapsed seconds for matched successful statements; total queue time).
5. **Differences outside the variable:** warm-up or not, cache setting, failures in one run only,
   capacity differences.
6. **What the tool cannot show:** the limits from SKILL.md that apply to this workload.
7. **Next checks** the user may want before deciding: rerun the largest regressions by hand with
   `EXPLAIN`, spot-check result sets, replay a second window.
