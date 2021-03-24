#!/bin/bash
cd $(dirname $0)
source ./00_config.ini

aws iam create-policy \
        --policy-name "${policy_name}" \
        --policy-document "$(cat iam_policy.json)" \
        --region ap-northeast-1 \
        --profile ${profile}   > ./log/create_policy_log.json
policy_arn="$(jq .Policy.Arn ./log/create_policy_log.json | tr -d '"')"

aws iam create-role \
    --role-name "${role_name}" \
    --assume-role-policy-document "$(cat assume_role.json)" \
    --region ap-northeast-1 \
    --profile ${profile}  > ./log/create_role_log.json


aws iam attach-role-policy \
    --role-name "${role_name}" \
    --policy-arn "${policy_arn}" \
    --region ap-northeast-1 \
    --profile ${profile}  > ./log/attach_policy_log.json
