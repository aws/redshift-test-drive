# Workload Replicator README

## Introduction

Customers are always trying to reproduce issues or workloads from clusters or to do what-if scenarios. A customer can easily clone a production cluster, but replicating the workload is more complicated. Workload Replicator was created to bridge that gap. Workload Replicator V2 enhances existing Workload Replicator tool by providing following additional functionalities: 

* Ability to mimic COPY and UNLOAD workloads. 
* Ability to execute the transactions and queries in the same time interval as executed in the source cluster. 

This enables the replay to be as close to the source run. It is **strongly recommended** to run Workload Replicator from a cloud EC2 instance.  

If you want to experiment with different Amazon Redshift cluster configurations to evaluate and compare how your workload performs you can use Amazon Redshift Node Configuration Comparison utility (https://github.com/aws-samples/amazon-redshift-config-compare) which invokes Workload Replicator utility. It provides ability to configure the necessary resources and will automatically execute the workload across N number of clusters.
For more details about this utility please check https://aws.amazon.com/blogs/big-data/compare-different-node-types-for-your-workload-using-amazon-redshift/

## Preparation

### Step 1 - Amazon Redshift production cluster setup

The first step is to enable audit logging in the Redshift production cluster. We’ll need all 3 types of logs: connection logs, user logs and user activity logs.

1. Using AWS Console, enable audit logging in the cluster specifying an S3 bucket location or cloudwatch location to save the log files   https://docs.aws.amazon.com/redshift/latest/mgmt/db-auditing.html
2. Change the parameter group `enable_user_activity_logging` to “true”.
3. Reboot the cluster
4. Take a snapshot of the source cluster prior to execution of the workload to be captured. This snapshot will be used to restore the target cluster, ensuring the target cluster is in the same state as the source cluster.

It may take around three hours for the audit logs to be delivered to S3.

### Step 2 - Workload Replicator setup

1. Create an EC2 instance
    1. Recommended EC2 instance type: **m5.8xlarge**, 32GB of SSD storage, Amazon Linux AMI
    2. The cluster must be accessible from where Workload Replicator is being run. This may entail modifying the security group inbound rules or running Workload Replicator on the same VPC as the Redshift replica cluster.
2. Install Workload Replicator and libraries dependencies on the provided EC2 machine
   1. Install Python3.
    Check if Python is already installed by doing ``which python3``. If the python3 binary is not found, then use:
    ```
    sudo yum install python3
    
    sudo yum install python3-pip
    ```
   2. Install ODBC dependencies
    ```
    sudo yum install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel
    ```
   3. (Skip this step if you have already cloned test-drive) Clone Workload Replicator scripts. Check if `git` is installed by doing ``which git``. If git binary cannot be found, then do ``yum install git`` before proceeding.
    ```
    git clone https://github.com/aws/redshift-test-drive.git
    cd redshift-test-drive/
    export REDSHIFT_TEST_DRIVE_ROOT=$(pwd)
    ```

   4. Install necessary Python libraries. In the root directory (`<directory you cloned the git repository into>/`), you will find the file requirements.txt. Run the following command
    ```
    cd $REDSHIFT_TEST_DRIVE_ROOT && make setup
    ```

   5. Follow the steps provided by the [documentation](https://docs.aws.amazon.com/redshift/latest/mgmt/configure-odbc-connection.html) and install ODBC Driver for Linux

   6. Check if AWS CLI is configured in the machine. If it’s not configured, follow the steps in [installation guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
   
   7. Configure AWS CLI:
      * Provided IAM user should have Redshift and S3 permissions. If temporary IAM credentials are being used, ensure they do not expire before the replay ends.
      * The IAM user needs to have permission to read the Audit logs S3 bucket configured in Step 1. This is required for the Extraction step of Workload Replicator.
      * The IAM user needs to have Redshift::GetClusterCredentials and redshift:DescribeLoggingStatus This is required for the Replay step of Workload Replicator
      * **IMPORTANT**: Default Region needs to be configured as well - use the region you intend to run the workload replicator against
    ```
    aws configure
    ```
                


### Step 3 - COPY and UNLOAD setup

You will need the following things setup for the COPY and UNLOAD process to execute correctly:

#### S3 bucket for UNLOAD commands

1. An S3 bucket where the UNLOAD command will store data to.
    If you don't already have one, create a new S3 bucket. Instructions to create a s3 bucket [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html).

2. IAM role with read access

    Create an IAM role with read access to S3 buckets where COPY commands read from. After you create this IAM role, add write access to the role for the S3 bucket in the previous step. Make sure the IAM role has a trust relationship with Redshift. This role will be attached to the replica cluster before running Workload Replicator. More information on IAM [here](https://docs.aws.amazon.com/redshift/latest/mgmt/copy-unload-iam-role.html).

## Extract
Extract executes a script that extracts query and connection information from user activity and connection log(retrieved from the audit logs). This is currently supported on both provisioned and serverless Redshift clusters. 

* Extract process relies on a customer specified YAML file (`extract.yaml`). You can find this YAML file under the `config` folder in the root directory (`<folder path to cloned directory>/redshift-test-drive/config`)
* If the source cluster end point is provided as input in the YAML file, Workload Replicator will automatically determine the location to extract the audit logs from, either it is S3 or Cloudwatch. Cloudwatch Audit Logs are now supported for both Provisioned Cluster and Serverless  
* Customer can provide the s3 bucket or local directory in YAML file as log location if they choose not to provide the source cluster endpoint
* Workload Replicator will extract starttime and endtime for each query from the system table automatically if the source cluster end point is provided as input in the YAML file. Recordtime from audit logs will be used otherwise. 
* The source cluster should be accessible from wherever Workload Replicator is being run. This may entail modifying the security group inbound rules to include “My IP”, or running Workload Replicator on an EC2 instance in the same VPC.

## To run an extract job, follow the steps below:

### Configure parameters 
Follow the table below to configure parameters in `extract.yaml` file found in in `$REDSHIFT_TEST_DRIVE_ROOT/config/` folder.

| Configuration value                                                                                                                         |Required?    | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |Example  |
|---------------------------------------------------------------------------------------------------------------------------------------------|---    |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---    |
| workload_location                                                                                                                           |Required    | Amazon S3 or local location. Where to save the extracted workload.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |"s3://mybucket/myworkload"  |
| start_time                                                                                                                                  |Required    | Start time of the workload to be extracted. If not provided process will extract workload from all the audit logs files available. [Default timezone is UTC, if timezone is not given in start_time then the value of start_time will be converted to UTC timezone based on Machine's current timezone]                                                                                                                                                                                                                                                                                     |“2020-07-24T09:31:00+00:00”  |
| end_time                                                                                                                                    |Required    | End time of the workload to be extracted. If not provided process will extract workload from all the audit logs files available.  [Default timezone is UTC, if timezone is not given in end_time then the value of end_time will be converted to UTC timezone based on Machine's current timezone]                                                                                                                                                                                                                                                                                          |“2020-07-26T21:45:00+00:00”  |
| Source cluster information and log location (Either the source cluster endpoint and admin user name OR the log location has to be provided) |
| source_cluster_endpoint                                                                                                                     |Optional    | If provided, Workload Replicator will use [`describe-logging-status`](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/redshift/describe-logging-status.html) to automatically retrieve the S3 audit log location. Additionally, Workload Replicator will query [SVL_STATEMENTTEXT](https://docs.aws.amazon.com/redshift/latest/dg/r_SVL_STATEMENTTEXT.html) to retrieve query start and end times. If this endpoint isn’t provided, or if the query cannot be found in SVL_STATEMENTTEXT, the record time present in the audit logs will be used for the query’s start and end times. |"<redshift-cluster-name>.<identifier>.<region>.redshift.amazonaws.com:<port>\<databasename>"  |
| master_username                                                                                                                             |Optional    | Required only if source_cluster_endpoint is provided.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |"awsuser"  |
| log_location                                                                                                                                |Optional    | Required if source_cluster_endpoint is not provided, since audit log location is inferred from the cluster or customer wants to use a local location pointing at the downloaded S3 audit logs.                                                                                                                                                                                                                                                                                                                                                                                              |""  |
| region                                                                                                                                      |Required    | Required if log location is provided for serverless.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |""  |
| odbc_driver                                                                                                                                 |Optional    | If provided and installed extraction will use ODBC . Otherwise Redshift python driver (redshit_connector) is used. Used only if source_cluster_endpoint is provided.                                                                                                                                                                                                                                                                                                                                                                                                                        |"Amazon Redshift (x86)"  |
| unload_system_table_queries                                                                                                                 |Optional    | If provided, this SQL file will be run at the end of the Extraction to UNLOAD system tables to the location provided in source_cluster_system_table_unload_location.                                                                                                                                                                                                                                                                                                                                                                                                                        |"unload_system_tables.sql"  |
| source_cluster_system_table_unload_location                                                                                                 |Optional    | Amazon S3 location to unload system tables for later analysis. Used only if source_cluster_endpoint is provided.                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |“s3://mybucket/myunload”  |
| source_cluster_system_table_unload_iam_role                                                                                                 |Optional    | Required only if source_cluster_system_table_unload_location is provided. IAM role to perform system table unloads to Amazon S3 and should have required access to the S3 location. Used only if source_cluster_endpoint is provided.                                                                                                                                                                                                                                                                                                                                                       |“arn:aws:iam::0123456789012:role/MyRedshiftUnloadRole”  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |""  
external_schemas                                                                                                 |Optional    | Add all the external_schemas in the form of a list and it is required only if the external sql statements are to be avoided in replay step.                                                                                                                                                                                                                                                                                                                                                      |[“external_schema_list”]  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |""   |

### Command

Once the above configuration parameters are set in extract.yaml, the workload from the source cluster can be extracted using the following command:

```
cd $REDSHIFT_TEST_DRIVE_ROOT && make extract
```

### Output

The extract functionality of the Workload Replicator produces the following output in the output location provided:

* sqls.json.gz
    * Contains the extracted SQL scripts.
* connections.json
    * Contains the extracted connections
* copy_replacements.csv
    * Contains the COPY locations found in the extracted workload. A replacement location may be specified to provide an alternate COPY location for replay. IAM role is mandatory to replay COPY workload.
* sql_statements_skipped.txt
    * Contains all the sql statement which are skipped during the replay process.

## Replay

Replay is the process of taking a workload extracted by Extract and replaying the same workload against a target cluster. Target cluster could be a Redshift Provisioned or Serverless cluster.
    
## To run Replay job, follow the steps below:

### Preparation
We will prepare the Redshift cluster / ecosystem for our Replay run first.
#### Replay on Provisioned 

* Restore the target cluster from the source cluster snapshot.
* The cluster must be accessible from wherever Workload Replicator is being run.
    This may entail modifying the security group inbound rules to include “My IP”, or running Workload Replicator on an EC2 instance in the same VPC.
* To execute COPY commands, the `execute_copy_statements` parameter must be set to `"true"`, and the “Replacement IAM role” column in the copy_replacements.csv file must have an IAM role for each row.
* Any UNLOAD/COPY command within stored procedures must be altered manually or removed to skip execution.

#### Replay on Serverless

* Restore the Serverless target cluster from the source cluster snapshot.
* Workload Replicator provides 2 different options to connect to target Redshift Serverless Cluster:
  * Target Cluster Endpoint: 
    * Cluster must be accessible from the system on which you're running Workload Replicator from 
    * This may entail modifying the security group inbound rules to include “My IP”, or running Workload Replicator on an EC2 instance in the same VPC.
    * Specify the value in ```target_cluster_endpoint```
  * NLB / NAT: 
    * This option provides ability to run the Workload Replicator from outside of your Cluster's VPC.
    * Provide NLB / NAT endpoint that has access to the Redshift Cluster.
    * Specify the value in ```nlb_nat_dns```
    * Value still must be provided for ```target_cluster_endpoint```
* One can optionally setup Secrets Manager which maps all individual users from extract to a single admin user. See "Setting up Secrets Manager" section for detailed steps.

### Replay for generating Analysis Report 

Replay also supports generation of pdf reports which enhances auditing in the Workload Replicator process to extract information about the errors that occurred, the validity of the run, and the performance of the replay.

#### Authorizing Access to Redshift using AWS Secrets Manager 
Follow below steps to setup the integration between Workload Replicator and AWS Secrets Manager. It can also be used to execute workloads which rely on Redshift's native IDP integration with non-IAM identity providers ( https://docs.aws.amazon.com/redshift/latest/mgmt/redshift-iam-access-control-native-idp.html )

NOTE: Setting up secrets manager is not required, but an optional step

* Configure admin username and password using AWS Secrets Manager - https://us-east-1.console.aws.amazon.com/secretsmanager/home
* Select "Other type of secret"
* Setup 1 secret with 2 Keys exactly as named below and provide their values:
  * admin_username
  * admin_password
* Confirm that the Role attached to EC2 from where Workload Replicator is being executed has GetSecretValue policy attached to it. It is needed for Secrets Manager. Attaching just this policy is a guideline that follows security advice of granting least required privilege 

### Configure parameters:
Follow the table below to configure parameters in `replay.yaml` file found in the `$REDSHIFT_TEST_DRIVE_ROOT/config/` folder.

| Configuration value                         |Required?     | Details                                                                                                                                                                                                                                                                                                           | Example                                                                                                                                                                                              |
|---------------------------------------------|---    |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tag                                         |Optional  | Custom identifier for this replay run.                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                      |
| workload_location                           |Required    | S3 or local. Location of the extracted workload to be replayed. Errors encountered during replay will be logged in a unique folder in the workload location.                                                                                                                                                      | “s3://mybucket/myworkload”                                                                                                                                                                           |
| target_cluster_endpoint                     |Required    | Cluster that will be used to replay the extracted workload.                                                                                                                                                                                                                                                       | Provisioned: “<redshift-cluster-name>.<identifier>.<region>.redshift.amazonaws.com:<port>/<databasename>” Serverless: “<accountid>.<region>.redshift-serverless.amazonaws.com:<port>/<databasename>” |
| master_username                             |Required    | This is necessary so `set session_authorization` can be successfully executed to mimic users during replay.                                                                                                                                                                                                       | "awsuser"                                                                                                                                                                                            |
| target_cluster_region                       |Required    | Region to which the target cluster belongs to.                                                                                                                                                                                                                                                                    | "us-east-1"                                                                                                                                                                                          |
| odbc_driver                                 |Optional    | Required only if ODBC connections are to be replayed, or if default_interface specifies “odbc”.                                                                                                                                                                                                                   | ""                                                                                                                                                                                                   |
| default_interface                           |Optional    | Currently, only playback using ODBC and psql are supported. If the connection log doesn’t specify the application name, or if an unsupported interface (e.g. JDBC) was used in the original workload, this interface will be used. Valid values are: **“psql”** or **"odbc". **Default value is set to** "psql"** | "psql"                                                                                                                                                                                               |
| time_interval_between_transactions          |Optional    | Leaving it as **“”** defers to connections.json. **“all on”** preserves time interval between transactions. **“all off”** ignores time interval between transactions, and executes them as a batch, back to back.                                                                                                 | ""                                                                                                                                                                                                   |
| time_interval_between_queries               |Optional    | Leaving it as **“”** defers to connections.json. **“all on”** preserves time interval between queries. **“all off”** ignores time interval between queries, and executes them as a batch, back to back.                                                                                                           | ""                                                                                                                                                                                                   |
| execute_copy_statements                     |Optional    | Whether or not COPY statements should be executed. Valid values are: **“true”** or **“false”**. Default value is **"false"**. Need to be set to **"true"** for copy to execute. Any UNLOAD/COPY command within stored procedures must be altered manually or removed to skip execution.                           | “false”                                                                                                                                                                                              |
| execute_unload_statements                   |Optional    | Whether or not UNLOAD statements should be executed. Valid values are: **“true”** or **“false”**. Any UNLOAD/COPY command within stored procedures must be altered manually or removed to skip execution.                                                                                                         | “false”                                                                                                                                                                                              |
| replay_output                               |Optional    | S3 Location for UNLOADs (all UNLOAD locations will be appended to this given location) and system table UNLOADs. Any UNLOAD/COPY command within stored procedures must be altered manually.                                                                                                                       | “s3://mybucket/myreplayoutput”                                                                                                                                                                       |
| analysis_output                             |Optional    | S3 Location for stl data to analyze the replay and produce analysis report                                                                                                                                                                                                                                        | “s3://mybucket/myreplayoutput”                                                                                                                                                                       |
| unload_iam_role                             |Optional    | Leaving this blank means UNLOAD statements will not be replayed. IAM role for UNLOADs to be replayed with.                                                                                                                                                                                                        | “arn:aws:iam::0123456789012:role/MyRedshiftUnloadRole”                                                                                                                                               |
| analysis_iam_role                           |Optional    | Leaving this blank means the replay will nto be analyzed.                                                                                                                                                                                                                                                         | “arn:aws:iam::0123456789012:role/MyRedshiftUnloadRole”                                                                                                                                               |
| unload_system_table_queries                 |Optional    | If provided, this SQL file will be run at the end of the Extraction to UNLOAD system tables to the location provided in replay_output.                                                                                                                                                                            | "unload_system_tables.sql"                                                                                                                                                                           |
| target_cluster_system_table_unload_iam_role |Optional    | IAM role to perform system table unloads to replay_output.                                                                                                                                                                                                                                                        | “arn:aws:iam::0123456789012:role/MyRedshiftUnloadRole”                                                                                                                                               |
| Include Exclude Filters                     |Optional    | The process can replay a subset of queries, filtered by including one or more lists of "databases AND users AND pids", or excluding one or more lists of "databases OR users OR pids".                                                                                                                            | ""                                                                                                                                                                                                   |
| log_level                                   |Required    | Default will be INFO. DEBUG can be used for additional logging.                                                                                                                                                                                                                                                   | debug                                                                                                                                                                                                |
| num_workers                                 |Optional    | Number of processes to use to parallelize the work. If omitted or null, uses one process per cpu - 1.                                                                                                                                                                                                             | “”                                                                                                                                                                                                   |
| connection_tolerance_sec                    |Optional    | Output warnings if connections are not within this number of seconds from their expected time.                                                                                                                                                                                                                    | “300”                                                                                                                                                                                                |
| backup_count                                |Optional    | Number of Workload Replicator logfiles to maintain                                                                                                                                                                                                                                                                       | 1                                                                                                                                                                                                    |
| drop_return                                 |Optional    | Discard the returned data from select statements at the driver level to avoid OOMs on EC2                                                                                                                                                                                                                         | true                                                                                                                                                                                                 |
| limit_concurrent_connections                |Optional    | To throtle the number of concurrent connections in the replay.                                                                                                                                                                                                                                                    | “300”                                                                                                                                                                                                |
| split_multi                                 |Optional    | To split the multi statement SQLs to address limitation with redshift_connector driver.                                                                                                                                                                                                                           | true                                                                                                                                                                                                 |
| secret_name                                 |Optional    | Name of the AWS Secret setup using AWS Secrets Manager.                                                                                                                                                                                                                                                           | “”                                                                                                                                                                                                   |
| nlb_nat_dns                                 |Optional    | NLB / NAT endpoint that will be used to connect to Target Cluster.                                                                                                                                                                                                                                                | “”                                                                                                                                                                                                   |


### Command

```
cd $REDSHIFT_TEST_DRIVE_ROOT && make replay
```

### Output

* Any errors from replay will be saved to workload_location provided in the `replay.yaml`
* Any output from UNLOADs will be saved to the replay_output provided in the `replay.yaml`
* Any system tables logs will be saved to the replay_output provided in the `replay.yaml`
* The analysis report will be saved to the analysis_output under analysis folder on s3
The analysis folder structure is as follows :
   * out
      - info.json: Cluster id, run start time, run end time, instance type, node count
     - replayid_report.pdf  
  * raw_data
    - raw csv files containing UNLOADed data
  * aggregated_data
    - formatted csv files as the data appears in the report
<br>
<br>


## Limitations 

* Dependent SQL queries across connections are not guaranteed to run in the original order.
* Spectrum queries are not replayed if the target cluster doesn’t have access to external tables
* COPY and UNLOAD command within stored procedures must be altered manually by the customers. 
* Replay using JDBC is not supported.
* If a connection’s session initiation or disconnection time are not found in the audit connection logs (e.g. outside of the specified `start_time` and `end_time`), the connection’s time is assumed to be the overall workload’s time.
* If a connection is not found in the audit connection log, but has queries associated with it in the user activity logs, the connection's `session_initiation_time` and `disconnection_time` are set to the overall workload's times. The connection will span the entire workload.
* There are cases where audit log capture internal Redshift re-writes of the queries. These queries might be replayed multiple times on the target as the duplicate entries in the logs are captured by the extract. 
* Limitations specific to Serverless:
  * Compilation time metric is not available for Serverless. So elapsed and execution times will include compilation time as well.
  * Commit time metric is not available for Serverless.
  * Replay analysis currently only supports CSV format. PDF report generation is work in progress.
* Workload Replicator does not support replaying federated users as this is a limitation for `GetClusterCredentials `API call.