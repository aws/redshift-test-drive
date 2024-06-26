# Replay Analysis README

## Introduction
The Replay analysis web app is used to analyze and compare replays. The goal of this tool is to facilitate understanding of Workload Replicator results and simplify analysis results for customers to make the right decisions for their use of Redshift.

## Preparation
### Prerequisites
* Execute replay (either using the [WorkloadReplicator](/core) or [NodeConfigCompare](/tools/NodeConfigCompare))
  * For workload replicator, execute replay by adding the following parameters in `$REDSHIFT_TEST_DRIVE_ROOT/config/replay.yaml`.
      * analysis_iam_role
      * analysis_output
  * For NodeConfigCompare, complete the Step Function execution.
* After the step function execution is complete (in case of NodeConfigCompare) or the replay is complete (in case of WorkloadReplicator), find the S3 location of the analysis files and copy to clipboard. Follow the following steps to find the location:
  * Navigate to Cloudwatch insights console located [here](https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:logs-insights)
  * Select the log group that is used by NodeConfigCompare or WorkloadReplicator
    * For NodeConfigCompare, the log group can be found in the CloudFormation console in the resources section with the CloudFormation template that was used for the NodeConfigCompare run.
  * Use the following insights query to find the S3 location where the Analysis files are present. Note: When you are asked to enter the analysis bucket below, use the path that is the closest ancestor to analysis folder i.e. if your analysis files are present in `s3://<bucket_name>/analysis/<analysis files>`, enter `s3://<bucket_name>`
```
fields @message
| filter @message like /can be used in Replay Analysis./
```
* Pre-install Node js (Minimum Node >= 14 required for React)
  * If you do not have Node js already installed, follow steps below:
    * If using EC2 instance, run following commands in order:
      * `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash`
      * `source ~/.bashrc`
      * `nvm install --lts`
      * Check that Node js is installed by running: `which node`
        
    * To install Node js in your local computer, follow [link](https://nodejs.org/en/download/package-manager/all) here.

* If using EC2 instance to view replay analysis web UI, ensure you allowlist your IP address to access the webpage hosted by EC2 instance by following these steps:
  * Follow this [link](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/working-with-security-groups.html#adding-security-group-rule) to configure inbound rules in the security group of your EC2 instance.
  * For **Type**, choose **Custom TCP**
  * For **Port Range**, enter 3000
  * For **Source**, select **My IP** to allow inbound traffic from only your local computer's public IPv4 address.
  * The inbound traffic should look like:
 <img width="831" alt="Screenshot 2024-05-13 at 2 57 57 PM" src="https://github.com/aws/redshift-test-drive/assets/121250701/30a5c6da-19a6-463e-985a-7e63678b83b3">

## Command
### NOTE: Complete all the initial setup steps outlined in the Redshift-test-drive Readme before proceeding.
Execute this from the root directory (within your clone of redshift-test-drive - this is aliased to `$REDSHIFT_TEST_DRIVE_ROOT`)
```
cd $REDSHIFT_TEST_DRIVE_ROOT && make replay_analysis
```

## Output
* Installs all the requirements required to launch the web app.
* Opens Web app which helps customer to choose multiple replays for comparison.

## User Interface of the Web App <br />
The start page of the interface will prompt users to provide the bucket location(s) with replays they want to analyze. It provides users the ability to select a number of replays for analysis. 

### Opening up the Web UI
* If you are using local computer, click the links generated in the terminal. You can access the web app using either  `http://localhost:3000`, or `http://YOUR-LOCAL-IP:3000`
* If using EC2 instance, identify the public IPv4 address of your instance:
  * Console option: Go to EC2 console and find your instance. Public IPv4 address of your instance is listed on the Networking tab.
  * Command line option: Use [describe-instances](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html#describe-instances) to find the public IPv4 address.
  * Open local browser and enter `http://YOUR-PUBLIC-IPV4-ADDRESS:3000`. The web link should look something like this: `http://12.123.123.1:3000/`

### Steps for using Web UI

* The start page will prompt user to add the following inputs:
    * Credentials Type <br />
    The credentials entered for accesing the analysis bucket can be either of the following:
        * Use a Profile <br />
         Enter user profile for the account where the Replay Bucket resides.
        * Use an IAM Role <br />
         Enter IAM role for the bucket mentioned in the file location. This IAM role should have read access to the bucket.
    * Replay analysis file location <br />
    Bucket where the analysis output lies which was pre-generated by running replay. This should be copied over from the step-2 of the pre-requisites section. 
    * Replays <br />
    List of replays available in the bucket for comparison
* Select the replays and click the Analysis button for generating the comparison analysis of the replay runs.

### Web UI Output
* Replay Analysis <br />
This section in the Web UI consists of following metrics:
    * Compare Throughput <br />
    It is a graph which showcases the number of queries executed per second. This data is filtered by the selected query types, users, and time range.
    * Aggregated Metrics <br />
    It is a table which displays the different percentiles of execution time, elapsed time, and queue time across selected replays. These values are representative of the selected query types, users, and time range.
    * Query Latency <br />
    It is a graph which displays the distribution of query latency.
    * Longest Running Queries<br />
    It is a table that shows the execution time metrics for each replay and also displays the top 100 running queries. 
* Replay Validation <br />
This section will give more insight into the success and validity of a given replay.Validity is defined by success and error rates, the distribution of errors, and differences in data ingested.It includes the following metrics for:
    * Query Errors <br />
    Errors encountered across selected replays.
    * Error Category Distribution <br />
    A Stacked bar chart that shows the distribution of errors that occurred across each replay and allow insight into which errors occurred most frequently.
    * COPY Ingestion Metrics <br />
    An aggregated execution metrics of COPY ingestion by replay.

