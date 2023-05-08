import boto3
import json
import cognitojwt


dynamo_client = boto3.client('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(event)

    user_id = event['pathParameters']['userId']
    
    itm = dynamo_client.get_item(
      TableName='columbia-coffee-chat-users',
      Key={'uuid':{'S':str(user_id)}}
    )
    
    #obj = s3.get_object(Bucket='columbia-coffee-chat-avatar-pic', Key=user_id+'.txt')
    
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
