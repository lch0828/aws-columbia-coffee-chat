import boto3
import json


COGNITO_APP_CLIENT_ID = '2djfekdv5ab536854jm5m8r2li'

cognito_client = boto3.client('cognito-idp')
dynamo_client = boto3.client('dynamodb')

def cognito_signup(username, email, password):
    res = cognito_client.sign_up(
        ClientId=COGNITO_APP_CLIENT_ID,
        Username=username,
        Password=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email,
            }
        ],
    )
    return res['UserSub']
    
def store_to_dynamo(uuid, username, fname, lname, email):
    user_info = {
        'uuid': {
            'S': uuid,
        },
        'uni': {
            'S': username,
        },
        'fname': {
            'S': fname,
        },
        'lname': {
            'S': lname,
        },
        'email': {
            'S': email,
        },
        'active_or_not': {
            'BOOL': True,
        },
    }
    dynamo_client.put_item(
        TableName='columbia-coffee-chat-users',
        Item=user_info,
    )
    
def lambda_handler(event, context):
    print("event[body]", event['body'])
    body = json.loads(event['body'])
    print("body:", body)
    
    username = body['username']
    email = body['email']
    password = body['password']
    fname = body['fname']
    lname = body['lname']
    
    uuid = cognito_signup(username, email, password)
    
    store_to_dynamo(uuid, username, fname, lname, email)
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps('lf1 cool')
    }
