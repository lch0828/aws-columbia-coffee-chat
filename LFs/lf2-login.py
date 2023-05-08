import boto3
import json


COGNITO_APP_CLIENT_ID = '2djfekdv5ab536854jm5m8r2li'

cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    username_or_email = body['username_or_email']
    password = body['password']
    
    print(body)
    
    res = cognito_client.initiate_auth(
        ClientId=COGNITO_APP_CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username_or_email,
            'PASSWORD': password
        }
    )
    
    print(res['AuthenticationResult']['IdToken'])
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps({
            'authToken': res['AuthenticationResult']['IdToken'],
            'status': True,
        }),
    }
