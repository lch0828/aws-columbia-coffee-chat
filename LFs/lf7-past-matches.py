import boto3
import cognitojwt
import json


dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    token = event['multiValueHeaders']['Authorization'][0]
    
    verified_claims: dict = cognitojwt.decode(
        token,
        'us-east-1',
        'us-east-1_VHCCaCEKX',
        testmode=True  # Disable token expiration check for testing purposes
    )

    print(verified_claims)
    user_id = verified_claims['sub']
    
    res1 = dynamo_client.query(
      TableName='columbia-coffee-chat-matches',
      IndexName='user_id1-index',
      ExpressionAttributeValues={
          ':v': {
              'S': user_id,
          },
      },
      KeyConditionExpression='user_id1 = :v',
    )
    
    res2 = dynamo_client.query(
      TableName='columbia-coffee-chat-matches',
      IndexName='user_id2-index',
      ExpressionAttributeValues={
          ':v': {
              'S': user_id,
          },
      },
      KeyConditionExpression='user_id2 = :v',
    )
    
    matches = res1.get('Items') + res2.get('Items')
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps({
            'matches': matches,
        })
    }
