import boto3
import json


dynamo_client = boto3.client('dynamodb')
table = boto3.resource('dynamodb').Table('columbia-coffee-chat-users')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    user = event['body']['profile']
    
    table.update_item(
        Key={'uuid': user['userId']},
        UpdateExpression="set active_or_not = :b, fname = :f, lname = :l, major = :m, program = :p, school_year = :y, phone = :ph, email = :e, classes = :c, interests = :i, date_pref = :d, time_pref = :t, location_pref = :lo, major_pref = :mp, program_pref = :pp, year_pref = :yp, classes_pref = :cp, interests_pref = :ip",
        ExpressionAttributeValues={
            ':b': user['active_or_not'],
            ':f': user['fname'],
            ':l': user['lname'],
            ':m': user['major'],
            ':p': user['program'],
            ':y': user['school_year'],
            ':ph': user['phone'],
            ':e': user['email'],
            ':c': user['classes'],
            ':i': user['interests'],
            ':d': user['date_pref'],
            ':t': user['time_pref'],
            ':lo': user['location_pref'],
            ':mp': user['major_pref'],
            ':pp': user['program_pref'],
            ':yp': user['year_pref'],
            ':cp': user['classes_pref'],
            ':ip': user['interests_pref']
        },
    )
    
    #s3.Object('columbia-coffee-chat-avatar-pic', user['userId'] + '.txt').put(Body=user['avatar_pic_base64'])
    
    itm = dynamo_client.get_item(
      TableName='columbia-coffee-chat-users',
      Key={'uuid':{'S':str(user['userId'])}}
    )
    
    print(itm['Item'])
    
    item = itm['Item']
    
    for i in item:
        for t in item[i]:
            if t != 'L':
                item[i] = item[i][t]
            else:
                item[i] = [x["S"] for x in item[i][t]]

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        'body': item
    }
