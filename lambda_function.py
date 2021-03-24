import json
import os
import boto3

rdsData       = boto3.client('rds-data')
cluster_arn   = os.environ['CLUSTER_ARN']
secret_arn    = os.environ['SECRET_ARN']
database_name = os.environ['DATABASE_NAME']
schema_name   = os.environ['SCHEMA_NAME']

# AuroraServerlessへのsql実行メソッド
def rds_exe_statement(exe_sql, param = [],tran_id = ""):
    return rdsData.execute_statement(
                    resourceArn = cluster_arn,
                    secretArn = secret_arn,
                    database = database_name,
                    sql = exe_sql,
                    parameters = param,
                    transactionId = tran_id)

def rds_begin_transaction():
    return rdsData.begin_transaction(
                        database = database_name,
                        resourceArn = cluster_arn,
                        schema = schema_name,
                        secretArn = secret_arn,
                        )

def rds_commit_transaction(tran_id):
    return rdsData.commit_transaction(
                        resourceArn = cluster_arn,
                        transactionId = tran_id,
                        secretArn = secret_arn,
                        )

def get_method(event):
    queryParam = event.get('queryStringParameters') # クエリパラメータ取得
    print(queryParam) # デバッグ用
    exe_statement_response = ""

    # クエリパラメータがない場合、クエリパラメータ(id)がない場合
    if queryParam == None or queryParam.get('id') == None:
        sql =  f"select * from {schema_name}.crud_test;"
        exe_statement_response = rds_exe_statement(exe_sql = sql)
    # クエリパラメータ(id)がある場合
    else:
        try:
            id = int(queryParam.get('id'))
        except:
            raise TypeError('id is type error')
        sql =  f"select * from {schema_name}.crud_test where id = :id;"
        param = [{'name': 'id', 'value': { 'longValue': id }}]
        exe_statement_response = rds_exe_statement(exe_sql = sql, param = param)

    message = exe_statement_response['records']
    return message

def post_method(event):
    body = event.get('body') # 更新パラメータ取得
    if body == None:
        raise # "パラメータがないならばエラー"

    body_load = json.loads(body)
    if body_load == None:
        raise # "パラメータがないならばエラー"
    if not 'content' in body_load:
        raise # "更新パラメータがないならばエラー"

    content = ""
    try:
        content = str(body_load['content'])
    except:
        raise TypeError('param type error')

    rds_transaction_info = rds_begin_transaction()
    transaction_id = rds_transaction_info['transactionId']

    sql = f"insert into {schema_name}.crud_test (content) values (:content);"
    param = [{'name': 'content', 'value': { 'stringValue': content }},]
    exe_statement_response = rds_exe_statement(exe_sql = sql,
                                               param = param,
                                               tran_id = transaction_id)

    print (f"transaction_id:{rds_transaction_info['transactionId']}") # debug

    commit_result = rds_commit_transaction(tran_id = transaction_id)

    print(commit_result)
    print(exe_statement_response)

    if commit_result['transactionStatus'] != 'Transaction Committed':
        #TODO:ロールバック処理
        raise

    message = exe_statement_response['generatedFields'] # 新規付番されたIDを返す
    return message

def patch_method(event):
    body = event.get('body') # 更新パラメータ取得
    if body == None:
         raise # "パラメータがないならばエラー"

    body_load = json.loads(body)

    if body_load == None:
        raise # "パラメータがないならばエラー"
    if not 'id' in body_load or not 'content' in body_load:
        raise # "パラメータがないならばエラー"

    id = ""
    content = ""
    try:
        id      = int(body_load['id'])
        content = str(body_load['content'])
    except:
        raise TypeError('param type error')

    rds_transaction_info = rds_begin_transaction()
    transaction_id = rds_transaction_info['transactionId']

    sql = f"update {schema_name}.crud_test set content = :content where id = :id;"
    param = [ {'name': 'id', 'value': { 'longValue': id }},
              {'name': 'content', 'value': { 'stringValue': content }},
    ]
    exe_statement_response = rds_exe_statement(exe_sql = sql,
                                               param = param,
                                               tran_id = transaction_id)

    # 1件以上更新されるのはerrorとすべき
    if exe_statement_response['numberOfRecordsUpdated'] != 1:
        #TODO:ロールバック処理
        raise

    print (f"transaction_id:{rds_transaction_info['transactionId']}") # debug

    commit_result = rds_commit_transaction(tran_id = transaction_id)

    if commit_result['transactionStatus'] != 'Transaction Committed':
        #TODO:ロールバック処理
        raise

    print(commit_result)  # debug
    print(exe_statement_response)  # debug

    message = f"update record number is {exe_statement_response['numberOfRecordsUpdated']} " #更新件数を返却

    return message

def delete_method(event):
    body = event.get('body') # 更新パラメータ取得
    if body == None:
         raise # "パラメータがないならばエラー"

    body_load = json.loads(body)
    if body_load == None:
        raise # "パラメータがないならばエラー"
    if not 'id' in body_load:
        raise # "パラメータがないならばエラー"

    id = ""
    try:
        id      = int(body_load['id'])
    except:
        raise TypeError('param type error')

    rds_transaction_info = rds_begin_transaction()
    transaction_id = rds_transaction_info['transactionId']

    # 元々データがない場合もエラーとならないけどめんどくさいので実装しない
    del_sql = f"delete from {schema_name}.crud_test where id = :id;"
    param = [{'name': 'id', 'value': { 'longValue': id }},
    ]

    del_exe_statement_response = rds_exe_statement(exe_sql = del_sql,
                                                   param = param,
                                                   tran_id = transaction_id)

    # 削除されたかわからないのでSELECT
    sel_sql = f"select * from {schema_name}.crud_test where id = :id"
    sel_exe_statement_responce = rds_exe_statement(exe_sql = sel_sql,
                                                   param = param,
                                                   tran_id = transaction_id)

    # 0件以外の場合はエラー
    if len(sel_exe_statement_responce['records']) != 0:
        #TODO:ロールバック処理
        raise

    commit_result = rds_commit_transaction(tran_id = transaction_id)

    print (f"transaction_id:{rds_transaction_info['transactionId']}") # debug
    print(commit_result) # debug

    if commit_result['transactionStatus'] != 'Transaction Committed':
        #TODO:ロールバック処理
        raise

    message = f'id:{id} is deleted' # 削除したキーを表示。

    return message


def handler(event, context):
    # main
    httpMethod = event.get('httpMethod') #httpMethod取得

    # デバッグ用
    print(event)
    print(httpMethod)

    # リクエストに応じて振り分け
    if httpMethod == None:
        return True

    http_method_map = {
        'GET'  : get_method,
        'POST' : post_method,
        'PATCH': patch_method,
        'DELETE': delete_method
    }


    res_message = ""
    try:
        res_message = http_method_map[httpMethod](event)
    except KeyError as e:
        raise ValueError('Invalid printer: {}'.format(httpMethod))

    return {
        'statusCode': 200,
        'body': json.dumps(res_message)
        }