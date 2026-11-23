# Patch validation and cache warming

The AWS Knowledge Center says that during a version upgrade Redshift clears its query and
compilation caches. The Developer Guide describes a remote compilation cache that persists after
cluster reboots, and an AWS blog on serverless compilation says upgraded clusters use that cache
with no warm-up needed, so the extra compile time after a patch is expected to be small. Measure
it; do not assume it. Test Drive can measure that effect before production gets the patch, or
pre-run the workload on a cluster before it takes over production traffic.

## Patch validation

A normal two-run comparison where the variable is the engine version:

1. Restore the baseline and the target from the same snapshot.
2. Keep the baseline on its current maintenance track; move the target with
   `aws redshift modify-cluster --maintenance-track-name <track>` and wait until it reports the
   new version.
3. Replay the same extract on both (see [run-extract-and-replay](run-extract-and-replay.md)).
4. Compare as in [results-and-interpretation](results-and-interpretation.md). The tool's reports do
   not break out compile time; query it on each restore while it exists:
   `SELECT COUNT(*), SUM(compile_time)/1e6 AS compile_s FROM sys_query_history WHERE start_time >= '<replay start>' AND query_text LIKE '%Test-Drive%';`
   `compile_time` exists on provisioned and Serverless.

## Cache warming

A replay warms only the cluster it runs against. AWS does not document that warming one
cluster speeds up another, so do not promise the user a benefit on production from warming a
copy.

A replay is never read-only. It runs every extracted statement, including INSERT, UPDATE, DELETE,
CTAS and DDL; `execute_copy_statements` and `execute_unload_statements` only hold back
statements whose text contains `from 's3:` or `to 's3:` (a literal substring match in
`core/replay/connection_thread.py`, `should_execute_sql`). A `CALL` is therefore never held back,
so COPY and UNLOAD inside stored procedures run against their original locations, and held-back
statements are counted as successes. So:

- Never replay against the live production cluster.
- On a cluster that will take over production (for example a resized or restored cluster before
  cut-over), the replay applies the window's writes to its data a second time. Warm it only if
  the user accepts that, or plans to restore or resynchronise its data after warming; ask first.
- Test Drive replays through the Python driver. JDBC and ODBC clients compile separately, so a
  replay may not warm what a JDBC or ODBC application uses.
- Pacing is fixed: the warm-up takes as long as the extracted window. Pick a window that contains
  the queries that matter most.
- Leaving `execute_copy_statements` and `execute_unload_statements` at `"false"` keeps the
  replay away from S3 data; it does not stop the other writes.
- To warm COPY and UNLOAD too, with the user's consent:
  - COPY: `execute_copy_statements: "true"` and a role in the third column ("Replacement IAM role")
    of every row of `copy_replacements.csv`. The file only has rows when the extract set
    `log_location` in `config/extract.yaml`.
  - UNLOAD: `execute_unload_statements: "true"`, `unload_iam_role`, and an S3 `replay_output`
    that the replayed UNLOADs are redirected into.
  - COPY and UNLOAD inside stored procedures are not redirected; they run against their original
    locations or must be removed by hand (`core/README.md` "Limitations").

Check the result afterwards on the warmed cluster: the share of statements with `compile_time = 0`
should rise when the same queries run again.
