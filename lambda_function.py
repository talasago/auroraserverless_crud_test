import json
import boto3

def lambda_handler(event, context):
    rdsData = boto3.client('rds-data')

    cluster_arn = 'arn:aws:rds:ap-northeast-1:398086303497:cluster:meigen-share-db'
    secret_arn = 'arn:aws:secretsmanager:ap-northeast-1:398086303497:secret:rds-db-credentials/cluster-WTXA7NF2XW2GIZC6UHOO2GAE3A/admin-nstzA9'
    database_name = 'meigen'

    # GET
    def get_proc():
        queryParam = event.get('queryStringParameters') # クエリパラメータ取得
        print(queryParam)

        message = ""
        if queryParam == None:
            rds_response = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "select * from FamousQoute")
            message = rds_response['records']

        elif queryParam.get('id') != None:
            try:
                id = int(queryParam.get('id'))
            except:
                raise  TypeError('id is type error')

            rds_response = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "select * from FamousQoute where id = :id",
                            parameters = [
                                {'name': 'id', 'value': { 'longValue': id }}
                            ]
                            )
            message = rds_response['records']

        else:
            rds_response = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "select * from FamousQoute")
            message = rds_response['records']
        return message

    # POST
    def post_proc():
        body = event.get('body') # 更新パラメータ取得
        if body == None:
            raise # "パラメータがないならばエラー"

        body_load = json.loads(body)
        print(body_load)
        print('user_id' in body_load)

        if body_load == None:
            raise # "パラメータがないならばエラー"
        if not 'user_id' in body_load or not 'content' in body_load:
            raise # "パラメータがないならばエラー"

        user_id = ""
        content = ""
        try:
            user_id = body_load['user_id']
            content = str(body_load['content'])
        except:
            raise TypeError('param type error')


        res_transaction = rdsData.begin_transaction(
                            database = 'meigen',
                            resourceArn = cluster_arn,
                            schema = 'meigen',
                            secretArn = secret_arn,
                            )
        transaction_id = res_transaction['transactionId']

        res_exe_statement = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "insert into FamousQoute  (user_id,content) values (:user_id, :content)",
                            parameters = [
                                {'name': 'user_id', 'value': { 'longValue': user_id }},
                                {'name': 'content', 'value': { 'stringValue': content }},
                            ]
                            )
        print("↓commit_transaction")
        print (transaction_id)
        commit_result = rdsData.commit_transaction(
                            resourceArn = cluster_arn,
                            transactionId = transaction_id,
                            secretArn = secret_arn,
                            )
        if commit_result['transactionStatus'] != 'Transaction Committed':
            #TODO:ロールバック処理
            raise

        print(commit_result)
        print(res_exe_statement)

        message = res_exe_statement['generatedFields']
        return message


    def patch_proc():
        message = ""
        body = event.get('body') # 更新パラメータ取得

        if body == None:
             raise # "パラメータがないならばエラー"

        body_load = json.loads(body)
        print(body_load)

        if body_load == None:
            raise # "パラメータがないならばエラー"
        if not 'id' in body_load or not 'user_id' in body_load or not 'content' in body_load:
            raise # "パラメータがないならばエラー"


        id = ""
        user_id = ""
        content = ""
        try:
            id      = body_load['id']
            user_id = body_load['user_id']
            content = str(body_load['content'])
        except:
            raise TypeError('param type error')

        res_transaction = rdsData.begin_transaction(
                            database = 'meigen',
                            resourceArn = cluster_arn,
                            schema = 'meigen',
                            secretArn = secret_arn,
                            )
        transaction_id = res_transaction['transactionId']

        res_exe_statement = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "update FamousQoute set content = :content where id = :id and user_id = :user_id",
                            parameters = [
                                {'name': 'id', 'value': { 'longValue': id }},
                                {'name': 'user_id', 'value': { 'longValue': user_id }},
                                {'name': 'content', 'value': { 'stringValue': content }},
                            ]
                            )

        # 1件以上更新されるのは現状errorとすべき
        if res_exe_statement['numberOfRecordsUpdated'] != 1:
            #TODO:ロールバック処理
            raise

        print(res_exe_statement)

        print("↓commit_transaction")
        print (transaction_id)
        commit_result = rdsData.commit_transaction(
                            resourceArn = cluster_arn,
                            transactionId = transaction_id,
                            secretArn = secret_arn,
                            )
        if commit_result['transactionStatus'] != 'Transaction Committed':
            #TODO:ロールバック処理
            raise

        message = res_exe_statement['numberOfRecordsUpdated']

        print(commit_result)

        return message


    # delete
    def delete_proc():
        message = ""
        body = event.get('body') # 更新パラメータ取得

        if body == None:
             raise # "パラメータがないならばエラー"

        body_load = json.loads(body)
        print(body_load)

        if body_load == None:
            raise # "パラメータがないならばエラー"
        if not 'id' in body_load or not 'user_id' in body_load:
            raise # "パラメータがないならばエラー"

        id = ""
        user_id = ""
        content = ""
        try:
            id      = body_load['id']
            user_id = body_load['user_id']
        except:
            raise TypeError('param type error')

        res_transaction = rdsData.begin_transaction(
                            database = 'meigen',
                            resourceArn = cluster_arn,
                            schema = 'meigen',
                            secretArn = secret_arn,
                            )
        transaction_id = res_transaction['transactionId']


        # 元々データがない場合もエラーとならないけどめんどくさいので実装しない

        res_del_exe_statement = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "delete from FamousQoute where id = :id and user_id = :user_id",
                            parameters = [
                                {'name': 'id', 'value': { 'longValue': id }},
                                {'name': 'user_id', 'value': { 'longValue': user_id }},
                            ]
                            )



        # 削除されたかわからないのでSELECT
        res_sel_exe_statement = rdsData.execute_statement(
                            resourceArn = cluster_arn,
                            secretArn = secret_arn,
                            database = database_name,
                            sql = "select * from FamousQoute where id = :id and user_id = :user_id",
                            parameters = [
                                {'name': 'id', 'value': { 'longValue': id }},
                                {'name': 'user_id', 'value': { 'longValue': user_id }},
                            ]
                            )

        print(res_sel_exe_statement['records'])

        # 0件以外の場合はエラー
        if len(res_sel_exe_statement['records']) != 0:
            #TODO:ロールバック処理
            raise


        print("↓commit_transaction")
        print (transaction_id)
        commit_result = rdsData.commit_transaction(
                            resourceArn = cluster_arn,
                            transactionId = transaction_id,
                            secretArn = secret_arn,
                            )
        if commit_result['transactionStatus'] != 'Transaction Committed':
            #TODO:ロールバック処理
            raise

        message = f'id:{id} of user_id:{user_id} is deleted'

        print(commit_result)

        return message


    # main
    httpMethod = event.get('httpMethod') #httpMethod取得

    # デバッグ用
    print(event)
    print(httpMethod)

    # リクエストに応じて振り分け
    if httpMethod == None:
        return True

    http_method_map = {
        'GET'  : get_proc,
        'POST' : post_proc,
        'PATCH': patch_proc,
        'DELETE': delete_proc
    }


    res_message = ""
    res_message = http_method_map[httpMethod]()

    try:
        res_message = http_method_map[httpMethod]()
    except KeyError as e:
        raise ValueError('Invalid printer: {}'.format(httpMethod))

    return {
        'statusCode': 200,
        'body': json.dumps(res_message)
        }