# Redshift Test Drive

## Introduction
Redshift Test Drive is an amalgamation of Redshift Replay and Node Config. The Redshift Replay consits of Workload Replicator, Replay Analysis and External Object Replicator.

## Prerequisites
Install the following packages before cloning the repository:
<br>1. Install git
<br> 
```
yum install git
```
 <br>2. Install pip3:
 <br>
 ```
 yum install pip3
 ```
 <br>3. Install make:
 <br>
 ```
 yum install make
 ```

 ## Preparations
 01. Clone the git repository using the following command:
 
 ```
 git clone https://github.com/aws/redshift-test-drive
 cd redshift-test-drive/
 export REDSHIFT_TEST_DRIVE_ROOT=$(pwd)
 ```
 02. Create a virtual environment inside the redshift-test-drive directory
 ```
 python3 -m venv testDriveEnv
 source testDriveEnv/bin/activate
 ```
 03. Execute the following command from the root directory to install all the required packages:
 ```
 cd $REDSHIFT_TEST_DRIVE_ROOT && make setup
 ```
 04. Refer to the Table of Content which will point out the different tools and README links of your interest.
 05. Finally after using the utility to run different benchmarks to deactivate virtual environment, run the following
 ```
 deactivate
 ```

<br>

### Table of Content
The following table provides links to all tools, locations & READMEs in the repository



| Index |                             Tool                              | Description | README links|
| ----- |:-------------------------------------------------------------:|-------| :-------: |
| 01|                 [Workload Replicator](/core)                  |Workload Replicator is an open source tool which helps customers to mimic their workloads on clusters |[README](/core/README.md)|
| 02|           [Replay Analysis](/tools/ReplayAnalysis)            |Replay Analysis utility enhances auditing in the Workload Replicator process to extract information about the errors that occurred, the validity of the run, and the performance of the replay. This is also a user interface in which customers can choose multiple replays to analyze, validate, and compare using the extracted audit logs.|[README](/tools/ReplayAnalysis/README.md)|
|03 | [External Object Replicator](/tools/ExternalObjectReplicator) |External Object Replicator replicates COPY manifest objects, and Spectrum object in the customer cluster|[README](/tools/ExternalObjectReplicator/README.md)|
|04|            [Node Config](/tools/NodeConfigCompare)            | Node Configuration Comparison utility answers a very common question on which instance type and number of nodes should we choose for your workload on Amazon Redshift.|[README](/tools/NodeConfigCompare/README.md)

## FAQs
Q. I'm experiencing issues with boto3 appearing as `ValueError: Invalid endpoint: https://s3..amazonaws.com` or something to that effect, how do I fix this?

A. `aws configure` command is a pre-requisite step for most tools within Test drive. Make sure you run `aws configure` and configure the default region.

----
Q. My make commands are failing with `make: *** No rule to make target `, how do I fix this?

A. Make sure you are in the right directory for execution. Make commands are made possible through the Makefile found in the root directory. If you followed the setup instructions, this is aliased to `REDSHIFT_TEST_DRIVE_ROOT` in your shell.

----

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

