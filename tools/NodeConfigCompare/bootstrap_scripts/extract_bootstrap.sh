#!/bin/bash
set -e
echo "bucket_name: $BUCKET_NAME"
echo "simple_replay_extract_overwrite_s3_path: $SIMPLE_REPLAY_EXTRACT_OVERWRITE_S3_PATH"
echo "simple_replay_log_location: $SIMPLE_REPLAY_LOG_LOCATION"
echo "redshift_user_name: $REDSHIFT_USER_NAME"
echo "what_if_timestamp: $WHAT_IF_TIMESTAMP"
echo "simple_replay_extract_start_time: $SIMPLE_REPLAY_EXTRACT_START_TIME"
echo "simple_replay_extract_end_time: $SIMPLE_REPLAY_EXTRACT_END_TIME"
echo "extract_prefix: $EXTRACT_PREFIX"
echo "script_prefix: $SCRIPT_PREFIX"

yum update -y
yum -y install git
yum -y install python3
yum -y install python3-pip
yum -y install aws-cfn-bootstrap
yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel
mkdir amazonutils
cd amazonutils
git clone https://github.com/aws/redshift-test-drive.git
cd redshift-test-drive
make setup
if [[ "$SIMPLE_REPLAY_EXTRACT_OVERWRITE_S3_PATH" != "N/A" ]]; then
  aws s3 cp $SIMPLE_REPLAY_EXTRACT_OVERWRITE_S3_PATH config/replay.yaml
fi
WORKLOAD_LOCATION="s3://${BUCKET_NAME}/${EXTRACT_PREFIX}/${WHAT_IF_TIMESTAMP}"
sed -i "s#master_username: \".*\"#master_username: \"$REDSHIFT_USER_NAME\"#g" config/extract.yaml
sed -i "s#log_location: \".*\"#log_location: \"$SIMPLE_REPLAY_LOG_LOCATION\"#g" config/extract.yaml
sed -i "s#workload_location: \".*\"#workload_location: \"$WORKLOAD_LOCATION\"#g" config/extract.yaml
sed -i "s#start_time: \".*\"#start_time: \"$SIMPLE_REPLAY_EXTRACT_START_TIME\"#g" config/extract.yaml
sed -i "s#end_time: \".*\"#end_time: \"$SIMPLE_REPLAY_EXTRACT_END_TIME\"#g" config/extract.yaml
aws s3 cp config/extract.yaml s3://$BUCKET_NAME/$SCRIPT_PREFIX/
make extract
