import boto3
import json
import cognitojwt

dynamo_client = boto3.client('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)
    
    token = event['multiValueHeaders']['Authorization'][0]

    
    # Sync mode
    verified_claims: dict = cognitojwt.decode(
        token,
        'us-east-1',
        'us-east-1_VHCCaCEKX',
        testmode=True  # Disable token expiration check for testing purposes
    )

    print(verified_claims)
    user_id = verified_claims['sub']
    
    itm = dynamo_client.get_item(
      TableName='columbia-coffee-chat-users',
      Key={'uuid':{'S':str(user_id)}}
    )
    
    #obj = s3.get_object(Bucket='columbia-coffee-chat-avatar-pic', Key=user_id+'.txt')
    
    #itm['Item'].pop('email')
    #itm['Item'].pop('active_or_not')
    #itm['Item'].pop('info_for_match')
    
    item = itm['Item']
    
    
    for i in item:
        for t in item[i]:
            if t != 'L':
                item[i] = item[i][t]
            else:
                item[i] = [x["S"] for x in item[i][t]]
    
    print(item)

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': json.dumps(item)
    }
