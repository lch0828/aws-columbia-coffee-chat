import boto3
import json


COGNITO_APP_CLIENT_ID = '2djfekdv5ab536854jm5m8r2li'

cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    username = body['username']
    confirmationCode = body['confirmation_code']
    
    cognito_client.confirm_sign_up(
        ClientId=COGNITO_APP_CLIENT_ID,
        Username=username,
        ConfirmationCode=confirmationCode,
    )
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps('lf1.5 cool')
    }
