# Cleanup

Deleting is the user's decision. Show the list, get a yes for each item, and delete only what
this run created. Verify each resource's identity first: account, region, ARN and the run tag
you set at creation (for example `test-drive-run=<id>`). A matching name is not enough.

## Checklist

1. **Account and region.** `aws sts get-caller-identity --query Account` and the region match the
   consent record.
2. **Provisioned restores.** For each baseline and target cluster, confirm the tag
   (`aws redshift describe-tags --resource-name <cluster-arn>`), then delete with a final
   snapshot by default:
   `aws redshift delete-cluster --cluster-identifier <id> --final-cluster-snapshot-identifier <id>-final`.
   Skip the final snapshot only when the user says so for that cluster.
3. **Serverless targets.** Confirm the tag
   (`aws redshift-serverless list-tags-for-resource --resource-arn <workgroup-arn>`), delete the
   workgroup, then the namespace with a final snapshot by default:
   `aws redshift-serverless delete-namespace --namespace-name <ns> --final-snapshot-name <ns>-final`.
4. **NodeConfigCompare runs.** Deleting its CloudFormation stack leaves the clusters, workgroups,
   namespaces and the stack's S3 bucket in place; delete those separately
   (`tools/NodeConfigCompare/README.md` "Clean up").
5. **Parameter groups.** If an existing non-production cluster was used and its parameter group
   was changed, re-attach the group it had before
   (`aws redshift modify-cluster --cluster-parameter-group-name <original>`) and reboot when the
   user agrees. Default parameter groups cannot be modified; they are re-attached, never edited.
   Delete custom groups created for the test once nothing uses them.
6. **Datashare grants.** If the producer granted the share to a target namespace for this run,
   ask the user whether to revoke it:
   `REVOKE USAGE ON DATASHARE <share> FROM NAMESPACE '<target-namespace-id>';` on the producer.
7. **S3.** Remove the run's prefixes only, never a whole bucket: the `Extraction_*` folder under
   `workload_location`, `replay_output`, `analysis_output`. They contain production SQL text;
   keep them only if the user asks, and say where they are.
8. **Host.** Copy off anything the user wants, then delete the logs under `core/logs/` and the
   files the tools leave in the repository root (`extract_logs.zip`, `replay_logs.zip`,
   `replay_worker_logs.zip`, `info.json`, `*_report.pdf`, `replayerrors000`); they contain
   statement text. Then terminate the EC2 instance. Remove IAM roles created only for
   the run.
9. **Source snapshot.** Delete it only if it was created for this run and the user no longer
   needs it.
10. **Verify.** List again: the clusters show `deleting` or are gone, the workgroups and
    namespaces are gone, the S3 prefixes are empty, the instance is terminated. Report anything
    still present.
