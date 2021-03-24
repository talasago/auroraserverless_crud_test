#!/bin/bash
cd $(dirname $0)
source ./00_config.ini

# 作成したAuroraServerlessのarnを取得
host=$(cat ./log/create_db_cluster_log.json | jq ".DBCluster.Endpoint" | tr -d '"')

aws secretsmanager create-secret \
                   --name "${secret_name}" \
                   --secret-string "{\"username\":\"${master_username}\",
                                     \"password\":\"${master_user_password}\",
                                     \"engine\":\"mysql\",
                                     \"host\":\"${host}\",
                                     \"port\":3306,
                                     \"dbClusterIdentifier\":\"${db_cluster_identifier}\"}" \
                   --region ap-northeast-1 \
                   --profile ${profile}   > ./log/create_secret_manager_log.json