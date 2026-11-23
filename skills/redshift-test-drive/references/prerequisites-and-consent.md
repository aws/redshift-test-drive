# Prerequisites and consent

Run these checks before the first `make extract`. Stop at the first one that fails and tell
the user what is missing; do not work around a failed check.

## Audit logging on the source

The extractor reads the **connection log** and the **user activity log**. AWS enables audit
logging as a set (connection, user and user activity logs); `core/README.md` "Preparation"
asks for all three.

Provisioned source:

```bash
aws redshift describe-logging-status --cluster-identifier <source-cluster> --region <region>
aws redshift describe-cluster-parameters --parameter-group-name <source-parameter-group> \
    --region <region> --query "Parameters[?ParameterName=='enable_user_activity_logging']"
```

`LoggingEnabled` must be true and the parameter value `true`. Changing the parameter needs a
reboot of the source; that is the user's decision, not yours.

Serverless source:

```bash
aws redshift-serverless get-namespace --namespace-name <namespace> --region <region> \
    --query 'namespace.logExports'
```

The list must contain both `useractivitylog` and `connectionlog`. The extractor reads them
from CloudWatch directly when the source endpoint contains `redshift-serverless`; there is no
export-to-S3 step.

Logs only exist from the moment logging was turned on. The upstream README notes that S3
delivery can take around three hours, so a window in the last few hours may still be
incomplete. Confirm the chosen window actually contains queries.

## Snapshot and host

- A snapshot of the source taken **before** the window to be replayed (`core/README.md`
  "Preparation"). The baseline and target are restored from it, so both start from the same data.
- The host can reach the source and target endpoints on their port, has the AWS CLI with a
  default region, and its credentials do not expire before the replay ends.
- The host's role has the permissions in `core/README.md` "IAM Permissions" (Serverless adds
  the `redshift-serverless:` actions listed there). A Serverless replay still calls
  `redshift:GetClusterCredentials` for the tool's own test connection, even with `secret_name` set.

## Two hard stops

**Production metrics as the baseline.** If the user wants to compare production
`sys_query_history` with one replay on the target, stop. Production has live concurrency, warm
caches and background work; a replay has none of that. Replay the same extract on a baseline
restore **and** on the target, and compare the two replays.

**A target with less compute.** If the target has fewer nodes or clearly less memory than the
baseline, it is expected to be slower. Say so before running. If the goal is to find the
smallest viable size, call it a right-sizing exercise and run it after a same-size comparison.

## Consent record

Ask, and write the answers down with the run (for example in the run's S3 prefix or the
ticket the user names). Do not start until every line has an answer.

| Item | Answer to record |
|---|---|
| Source | Cluster or workgroup id, region, account |
| Window | `start_time` and `end_time`, ISO 8601 with offset |
| Baseline and target | Which restore is baseline, which is target, and the one difference between them |
| Not production | The user confirms both replay targets are restores they may change and delete |
| COPY / UNLOAD | Off (default), or on with the replacement locations and IAM roles supplied |
| Workload storage | The S3 bucket and prefix where `SQLs.json.gz` and `connections.json` may live |
| Cost | Accepted: target hours, host hours, S3 storage; each replay lasts about as long as the window |
| Cleanup | Who deletes the targets, the host and the S3 prefix, and when |

## Data handling

`SQLs.json.gz` and `connections.json` contain the production SQL text, including literals, and
the database user names. Keep them in the bucket the user named, with that bucket's encryption
and access policy; do not copy them to local disk, chat or tickets beyond what a step needs.
Analysis outputs under `analysis_output`, and the `connection_errors/` and `transaction_errors/`
files a replay writes under `workload_location`, contain query text too. Delete all of it at cleanup
unless the user asks to keep it.
