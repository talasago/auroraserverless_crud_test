#!/bin/bash
#
# 前提条件
# 作成済みのvpcが存在すること

cd $(dirname $0)
source ./00_config.ini

aws rds create-db-cluster \
            --backup-retention-period "1" \
            --copy-tags-to-snapshot \
            --db-cluster-identifier "${db_cluster_identifier}" \
            --db-cluster-parameter-group-name "default.aurora-mysql5.7" \
            --db-subnet-group-name "${subnet_group_name}" \
            --database-name "${database_name}" \
            --no-deletion-protection  \
            --engine "aurora-mysql" \
            --engine-mode "serverless" \
            --engine-version "5.7.mysql_aurora.2.07.1" \
            --master-user-password "${master_user_password}" \
            --master-username "${master_username}" \
            --pre-signed-url "" \
            --storage-encrypted  \
            --enable-http-endpoint \
            --region ap-northeast-1 \
            --profile ${profile}   > ./log/create_db_cluster_log.json
