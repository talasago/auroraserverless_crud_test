#!/bin/bash
cd $(dirname $0)
source ./00_config.ini

role_arn=$(jq .Role.Arn ./log/create_role_log.json  | tr -d '"')
lambda_arn=$(jq .FunctionArn ./log/create_lambda.log | tr -d '"')
lambda_uri="arn:aws:apigateway:ap-northeast-1:lambda:path/2015-03-31/functions/${lambda_arn}/invocations"

aws apigateway create-rest-api \
    --name "${api_name}" \
    --endpoint-configuration '{ "types": ["REGIONAL"] }' \
    --region ap-northeast-1 \
    --profile ${profile}  > ./log/create_rest_api.json

rest_api_id=$(jq .id ./log/create_rest_api.json | tr -d '"')

aws apigateway get-resources \
    --embed "methods" \
    --rest-api-id "${rest_api_id}" \
    --region ap-northeast-1 \
    --profile ${profile}  > ./log/get_resources.json

resource_id=$(jq .items[0].id ./log/get_resources.json | tr -d '"')

function create_method_and_integration() {
    local _http_method=$1
    local _put_method_option=$2

    aws apigateway put-method \
        --authorization-type "NONE" \
        --rest-api-id "${rest_api_id}" \
        --resource-id "${resource_id}" \
        --http-method "${_http_method}" \
        --region ap-northeast-1 \
        ${_put_method_option} \
        --profile ${profile}  > ./log/put_method_${_http_method}.json

     aws apigateway put-method-response \
        --response-models '{"application/json":"Empty"}' \
        --rest-api-id "${rest_api_id}" \
        --resource-id "${resource_id}" \
        --http-method "${_http_method}" \
        --status-code "200" \
        --region ap-northeast-1 \
        --profile ${profile}  > ./log/put_method_res_get_${_http_method}.json

#新しいメソッドの統合ポイントは画面上から設定すること

#    aws apigateway put-integration \
#        --type "AWS_PROXY" \
#        --rest-api-id "${rest_api_id}" \
#        --resource-id "${resource_id}" \
#        --http-method "${_http_method}" \
#        --integration-http-method "POST" \
#        --uri ${lambda_uri} \
#        --region ap-northeast-1 \
#        --credentials ${role_arn} \
#        --profile ${profile}  > ./log/put_integration_get_${_http_method}.json
#        # ラメータ追加する
#    #  --request-parameters "integration.request.path.id=method.request.path.id" \
#
#    aws apigateway put-integration-response \
#        --response-templates '{"application/json":"Empty"}' \
#        --rest-api-id "${rest_api_id}" \
#        --resource-id "${resource_id}" \
#        --http-method "${_http_method}" \
#        --status-code "200" \
#        --region ap-northeast-1 \
#        --profile ${profile}  > ./log/put_integration_get_${_http_method}.json
}

create_method_and_integration "GET" "--request-parameters method.request.querystring.id=False"
create_method_and_integration "POST"
create_method_and_integration "DELETE"
create_method_and_integration "PATCH"

#TODO:デプロイ