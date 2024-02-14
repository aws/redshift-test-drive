# External Object Replicator README

## Introduction
External Object Replicator replicates COPY commands objects, Copy manifest objects, and Spectrum 
objects in source cluster to the target s3 location.

External object replicator clones/replicates the following objects to target s3 location:
1. COPY objects accessed by the source cluster when user runs COPY command. 
   - For example, when `copy category
   from 's3://mybucket/custdata' ` is run on source cluster, `s3://mybucket/custdata` will be cloned to target location by external object replicator.
2. COPY manifest files accessed by source cluster when user uses a manifest files to load multiple files
   - Files specified in a manifest file will all be replicated to target s3 location
3. Spectrum objects queried by source cluster
   - Spectrum files will be replicated in the targe s3 location
   - Spectrum objects(tables and schemas) will be replicated in a new cloned Glue database

The utility is currently only supported on provisioned Redshift. We plan to increase the functionality to support 
serverless endpoint in a future release.

## Preparation

### External Object Replicator setup

1. Create an EC2 instance
    1. Recommended EC2 instance type: **m5.8xlarge**, 32GB of SSD storage, Amazon Linux AMI
    2. The cluster must be accessible from where External object replicator is being run. This may entail modifying the security group inbound rules or running Workload Replicator on the same VPC as the Redshift replica cluster. 
2. Install Workload Replicator and libraries dependencies on the provided EC2 machine by following the instructions [here](/core/README.md#step-2---workload-replicator-setup)


## Running External Object Replicator

* External Object Replicator currently only supports Redshift Provisioned cluster
* External Object Replicator will replicate any files copied using the COPY command or a MANIFEST file, and Spectrum tables queried within the starttime and endtime provided in the external_replicator.yaml (See below).
* The source cluster should be accessible from wherever External Object Replicator is being run. This may entail modifying the security group inbound rules to include “My IP”, or running Workload Replicator on an EC2 instance in the same VPC.

### To run external object replicator, begin by configuring the parameters in `$REDSHIFT_TEST_DRIVE_ROOT/config/external_object_replicator.yaml`:

| Configuration value          | Required?   | Details                                                                                                                                                                                                       | Example                                                                                      |
|------------------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| source_cluster_endpoint      | Required    | Redshift source cluster endpoint                                                                                                                                                                              | "<redshift-cluster-name>.<identifier>.<region>.redshift.amazonaws.com:<port>\<databasename>" |
| region                       | Required    | Region of the source cluster                                                                                                                                                                                  | "us-east-1"                                                                                  |
| redshift_user                | Required    | Username to access the cluster and database                                                                                                                                                                   | "awsuser"                                                                                    |
| start_time                   | Required    | Start time of the workload to be replicated. [Default timezone is UTC, if timezone is not given in end_time then the value of end_time will be converted to UTC timezone based on Machine's current timezone] | “2020-07-26T21:45:00+00:00”                                                                  |
| end_time                     | Required    | Start time of the workload to be replicated. [Default timezone is UTC, if timezone is not given in end_time then the value of end_time will be converted to UTC timezone based on Machine's current timezone] | “2020-07-27T21:45:00+00:00”                                                                  |
| target_s3_location           | Required    | A S3 bucket location where you want the replicator to store cloned objects                                                                                                                                    | "s3://mybucket/myworkload"                                                                   |
| log_level                    | Required    | Specify desired log level - you have the option of INFO and DEBUG                                                                                                                                             | "DEBUG"                                                                                      |

### Command

Once the above configuration parameters are set in external_object_replicator.yaml, the tool can be run using the following command

```
cd $REDSHIFT_TEST_DRIVE_ROOT && make external_object_replicator
```

### Output

External Replicator produces the following outputs:
  
In the target_S3_location provided in external_replicator.yaml:
* COPY objects in copyfiles/
  * COPY objects cloned by the external replicator are all located within the directory of copyfiles/
* Final_Copy_Objects.csv in copyfiles/
  * A CSV file containing details of COPY objects cloned
* Spectrum files in Spectrumfiles/ 
  * Spectrum files cloned by the external replicator are all located within the directory of Spectrumfiles/
* Spectrum_objects_copy_report.csv in Spectrumfiles/ 
  *  A CSV file containing details of Spectrum objects cloned

In the local directory:
* external_replicator.log
    * Logs produced by the execution of external replicator.
 
## Cleanup
To avoid unwanted costs incurring post execution, we recommend deleting the following resources:
* If S3 bucket was created, delete the s3 bucket
* Delete EC2 Instance created


