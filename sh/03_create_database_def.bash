#!/bin/bash
# auroraserverlessのデータベース情報（スキーマ、テーブル定義）を作成
# 前提条件：Auroraserverlessクラスターが作成され準備完了となっていること
cd $(dirname $0)
source ./00_config.ini

db_cluster_arn=$(jq .DBCluster.DBClusterArn ./log/create_db_cluster_log.json | tr -d '"')
secret_arn=$(jq .ARN ./log/create_secret_manager_log.json | tr -d '"')

aws rds-data execute-statement \
    --resource-arn "${db_cluster_arn}" \
    --secret-arn "${secret_arn}" \
    --sql "create database ${schema_name}" \
    --profile ${profile}  > ./log/create_mysql_database.json


aws rds-data execute-statement \
    --resource-arn "${db_cluster_arn}" \
    --secret-arn "${secret_arn}" \
    --sql "create table ${schema_name}.crud_test(id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
                                                 content nvarchar(200));" \
    --profile ${profile}  > ./log/create_mysql_table.json
