#!/bin/bash
cd $(dirname $0)
source ./00_config.ini

role_arn=$(jq .Role.Arn ./log/create_role_log.json  | tr -d '"')
db_cluster_arn=$(jq .DBCluster.DBClusterArn  ./log/create_db_cluster_log.json | tr -d '"')
secret_arn=$(jq .ARN ./log/create_secret_manager_log.json | tr -d '"')

zip app.zip ../lambda_function.py

aws lambda create-function \
    --function-name "${func_name}" \
    --runtime python3.8 \
    --zip-file fileb://app.zip \
    --handler lambda_function.handler \
    --role ${role_arn} \
    --profile ${profile} > ./log/create_lambda.log

aws lambda update-function-configuration \
    --function-name "${func_name}" \
    --environment Variables="{CLUSTER_ARN=${db_cluster_arn},
                             SECRET_ARN=${secret_arn},
                             DATABASE_NAME=${database_name},
                             SCHEMA_NAME=${schema_name}}" \
    --profile ${profile} > ./log/update_func_conf.log

rm app.zip