# Target setup

## Contents

- [The equal-compute rule](#the-equal-compute-rule)
- [Restore the baseline and the target](#restore-the-baseline-and-the-target)
- [Apply the change under test](#apply-the-change-under-test)
- [Hold everything else constant](#hold-everything-else-constant)
- [Warm-up run](#warm-up-run)
- [Alerts to give before running](#alerts-to-give-before-running)
- [Three or more candidates](#three-or-more-candidates)

## The equal-compute rule

Change one thing. Baseline and target are restored from the same snapshot, replay the same
`Extraction_*` folder, and differ only in the configuration under test.

- Record both configurations before the first replay:
  `aws redshift describe-clusters --cluster-identifier <id> --query 'Clusters[0].{NodeType:NodeType,Nodes:NumberOfNodes}'`
  or `aws redshift-serverless get-workgroup --workgroup-name <wg> --query 'workgroup.baseCapacity'`.
  These go next to every number you report.
- Changing node type: keep the node count unless the count is the variable. Different node
  types have different vCPU, memory and slice counts per node; look them up in the AWS
  documentation and report them, because a gain can come from extra capacity rather than the
  node type itself.
- A target with less compute than the baseline is expected to regress. Say so before running.
- Moving off DC2: DC2 keeps data on local SSD, RA3 and RG use managed storage, so a restored
  target starts with a cold result cache and local compile cache (AWS: a restore from the latest
  DC2 snapshot pre-loads the hottest blocks). Match total memory rather than node count, and plan
  a warm-up run.

## Restore the baseline and the target

From a snapshot taken before the extracted window (`core/README.md`, Replay, "Preparation"):

```bash
aws redshift restore-from-cluster-snapshot --cluster-identifier <baseline-id> \
    --snapshot-identifier <snapshot> --region <region>
aws redshift restore-from-cluster-snapshot --cluster-identifier <target-id> \
    --snapshot-identifier <snapshot> --node-type <node-type> --number-of-nodes <n> --region <region>
```

A Serverless target is restored into its own namespace and workgroup; create both first, since
`restore-from-snapshot` restores into an existing namespace:

```bash
aws redshift-serverless restore-from-snapshot --namespace-name <ns> --workgroup-name <wg> \
    --snapshot-arn <provisioned-snapshot-arn> --region <region>
```

Restores must be reachable from the host. Tag them with the run (for example `test-drive-run=<id>`)
so [cleanup](cleanup.md) can verify what it deletes.

## Apply the change under test

| Change | How |
|---|---|
| Manual vs Auto WLM | Create a custom parameter group (its default `wlm_json_configuration` is `[{"auto_wlm":true}]`), set the WLM JSON you test, attach it with `aws redshift modify-cluster --cluster-parameter-group-name`, reboot, and check `ParameterApplyStatus` is `in-sync`. Never modify a default parameter group. |
| Multi-queue manual to Auto | Suggest an intermediate run with a single manual queue: it separates queue consolidation from the Auto WLM algorithm |
| Node type or count | `restore-from-cluster-snapshot` with `--node-type`/`--number-of-nodes` (above), or `aws redshift resize-cluster` on an existing restore |
| Provisioned to Serverless | Restore the provisioned snapshot into a namespace and workgroup (above) |
| Serverless base capacity | `aws redshift-serverless update-workgroup --workgroup-name <wg> --base-capacity <rpu>`; wait for the workgroup to be `AVAILABLE` |
| New patch | `aws redshift modify-cluster --maintenance-track-name <track>` on the target; see [patch-validation-and-cache-warming](patch-validation-and-cache-warming.md) |
| Datashare consumer size | See [datashare-consumer](datashare-consumer.md) |
| Existing non-production endpoint | Allowed if the user confirms it is not production and may change; record its configuration as above |

Manual WLM exists only on provisioned clusters. A Serverless target has no WLM queues to
configure; its variable is base capacity.

## Hold everything else constant

- **Concurrency scaling:** it is enabled per queue in the WLM JSON (`concurrency_scaling`);
  make each queue's setting identical on both. `max_concurrency_scaling_clusters` only caps it:
  set it to the same value in both parameter groups. It is a parameter-group parameter, not a
  `modify-cluster` option.
- **Result cache:** decide whether the comparison runs with it on or off and make it identical
  on both. To turn it off for the replayed users:
  `ALTER USER <user> SET enable_result_cache_for_session TO off;` on both restores.
- **Parameter group:** identical apart from the variable under test.
- **Maintenance track:** identical unless the patch is the variable.

## Warm-up run

A restore starts with a cold result cache and local compile cache. When node types differ,
after a DC2 move, or before validating a patch, replay once on each restore with `tag` set to
`warmup-<name>` and without `analysis_output`, then run the measured replays with the real tags. Warm both, not only the
target: a replay also re-runs the workload's writes, so warming one side alone leaves the two
restores with different data. Skip the warm-up when comparing two WLM settings on restores that
have already run the workload equally, or when cold-start behaviour is the thing being measured.
Tell the user a warm-up doubles the replay time on each restore.

## Alerts to give before running

Present these together, after the configurations are known and before the first replay.
They are warnings, not blocks.

- The window is under 30 minutes: it may miss the workload's variety; suggest 1–4 hours around the peak.
- The extract is more than 30 days old: tables, data volumes and queries may have changed; suggest re-extracting.
- Node count or total memory differs between baseline and target by more than about 20%:
  results will mix the configuration change with a capacity change.
- Only one Serverless base capacity is being tested: suggest two or three values.

## Three or more candidates

For three or more configurations (node types, RPU sizes, WLM variants, datashare consumer
sizes), propose NodeConfigCompare (`tools/NodeConfigCompare/README.md`). It creates the
clusters and workgroups, runs the replays and builds the comparison views. It pauses
provisioned clusters afterwards when `AUTO_PAUSE` is true; the user deletes the clusters,
workgroups and namespaces.
