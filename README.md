# Redshift Test Drive

## Introduction
Redshift Test Drive is an amalgation of Redshift Replay and Node Config. The Redshift Replay consits of Workload Replicator, Replay Analysis and External Object Replicator.

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
 git clone git@github.com:aws/redshift-test-drive.git
 ```
 02. Execute the following command from the root directory to install all the required packages:
 ```
 make setup
 ```
 03. Refer to the Table of Content which will point out the different tools and README links of your interest.


<br>

### Table of Content
The following table provides links to all READMEs in the repository



| Index      | Tool | Description | README links|
| ----------- | :-----------: |-------| :-------: |
| 01      | Workload Replicator       |Workload Replicator is an open source tool which helps customers to mimic their workloads on clusters |[README](/core/README.md)|
| 02   | Replay Analysis        |Replay Analysis utility enhances auditing in the Workload Replicator process to extract information about the errors that occurred, the validity of the run, and the performance of the replay. This is also a user interface in which customers can choose multiple replays to analyze, validate, and compare using the extracted audit logs.|[README](/tools/ReplayAnalysis/README.md)|
|03 | External Object Replicator |External Object Replicator replicates COPY manifest objects, and Spectrum object in the customer cluster|[README](/tools/ExternalObjectReplicator/README.md)|
|04|Node Config| Node Configuration Comparison utility answers a very common question on which instance type and number of nodes should we choose for your workload on Amazon Redshift.|[README](/tools/NodeConfigCompare/README.md)


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

