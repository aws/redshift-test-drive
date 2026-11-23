# Replaying on a datashare consumer

Use this when the workload runs on a consumer that reads producer data through a datashare,
and the comparison is between consumer configurations (node type, count, base capacity).
Data sharing needs RA3 or RG node types, or Serverless, on both sides; DC2 cannot be a producer or a consumer.

## Which database a replayed statement runs in

The replayer opens each session in the database recorded for that connection in
`connections.json`, not in the database of `target_cluster_endpoint`. So the target consumer
must offer every database the workload connected to, under the same name:

- If the workload connected to the datashare database itself (for example `sales_share`),
  create the consumer database from the datashare with that exact name on the target.
- If the workload connected to a local database (for example `dev`) and reached shared tables
  through a local external schema and `search_path`, recreate that schema and `search_path`
  on the target (below).

The database in `target_cluster_endpoint` is used for the tool's own test and analysis
connections. Point it at a local database such as `dev`, not at the datashare database.

## Re-establish the datashare on the restored consumer

A Test Drive target is always a new cluster or namespace, so it keeps the consumer's local
objects but not its datashare access (AWS keeps datashare access only when a Serverless snapshot
is restored into the same namespace). Two steps, the first on the producer:

1. On the producer, grant the share to the target's namespace. This changes the producer, so
   get the user's consent first. Run it as a single statement, outside a transaction block:
   `GRANT USAGE ON DATASHARE <share> TO NAMESPACE '<target-namespace-id>';`
   The namespace id is `aws redshift-serverless get-namespace --namespace-name <ns> --query 'namespace.namespaceId'`
   or the last part of `ClusterNamespaceArn` from `aws redshift describe-clusters`.
2. On the target consumer, check for a stale database first with
   `SELECT database_name, database_type FROM svv_redshift_databases WHERE database_name = '<share_db>';`.
   If it is listed, drop it with `DROP DATABASE <share_db>;` (Redshift has no `IF EXISTS` here,
   and `DROP DATABASE` cannot run inside a transaction block). Then recreate it the same way the
   source has it:

```sql
CREATE DATABASE <share_db> FROM DATASHARE <share> OF NAMESPACE '<producer-namespace-id>';
GRANT USAGE ON DATABASE <share_db> TO <workload_user>;
```

Repeat the grant for every workload user and for `master_username`. If the source database was
created `WITH PERMISSIONS`, recreate it that way and repeat the source's object-level grants;
without it, usage on the database gives access to all shared objects.

## Local external schema and search_path

When the workload's sessions run in a local database and use unqualified names:

```sql
CREATE EXTERNAL SCHEMA <ext_schema> FROM REDSHIFT DATABASE '<share_db>' SCHEMA '<producer_schema>';
GRANT USAGE ON SCHEMA <ext_schema> TO <workload_user>;
ALTER USER <workload_user> SET search_path TO <ext_schema>, public;
```

Copy the schema name and `search_path` from the source consumer rather than inventing new ones,
so the replayed statements resolve exactly as they did in production.

Check before replaying, as a workload user: `SHOW search_path;` and a `SELECT COUNT(*)` on one
shared table through the name the workload uses.

## Limits to tell the user

- Replayed writes to shared objects fail on the baseline and the target alike when the share is
  read-only. If the producer granted write access (INSERT, UPDATE and similar) to the consumer
  namespace, those writes change the producer's live data. `SVV_DATASHARE_PRIVILEGES` shows only
  ALTER and SHARE on the share itself, so check the producer's `GRANT ... TO DATASHARE`
  statements or the datashare's permissions page in the console with the user, and, for a share
  from another account, whether the consumer namespace was associated with `--allow-writes`.
  Do not replay a writing workload against a production producer.
- Producer load is part of every measurement. If the producer is the bottleneck it masks
  consumer-side differences.
- Replay the baseline and target one after the other, not at the same time, so they do not
  compete for the producer.

## NodeConfigCompare datashare mode

For several consumer configurations, NodeConfigCompare's datashare mode
(`tools/NodeConfigCompare/README.md` "Datashare Mode") restores each candidate, re-establishes
the datashare, routes replay queries to the datashare database and management work to a local
database, and reports comparative metrics. Its documented limits:

- It needs an existing producer with an active datashare, a subscribed consumer with audit
  logging on, and a consumer snapshot.
- Only the consumer side varies; the producer is fixed.
- The producer must be a provisioned cluster.
- Producer and consumer must be in the same AWS account.
- It does not recommend or select a configuration.
