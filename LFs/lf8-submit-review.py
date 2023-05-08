import boto3
import json


dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    match_id = body['match_id']
    review = body['review']
    
    
    dynamo_client.update_item(
        TableName='columbia-coffee-chat-matches',
        Key={
            'match_id': {
                'S': match_id,
            },
        },
        AttributeUpdates={
            'review': {
                'Value': {
                    'S': review,
                },
                'Action': 'PUT'
            },
        },
    )
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps('lf8 cool')
    }
