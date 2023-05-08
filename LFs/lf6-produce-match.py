import boto3
from botocore.exceptions import ClientError
import json
import random
import datetime


dynamo_client = boto3.client('dynamodb')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    URL = 'https://sqs.us-east-1.amazonaws.com/094343250950/match-email'

    # get active users
    table_name = 'columbia-coffee-chat-users'
    filter_expression = 'active_or_not = :active_or_not'
    expression_attribute_values = {':active_or_not': {'BOOL': True}}
    query_params = {
        'TableName': table_name,
        'FilterExpression': filter_expression,
        'ExpressionAttributeValues': expression_attribute_values
    }
    
    response = dynamo_client.scan(**query_params)
    usrs = response['Items']
    print(usrs)
    
    # randomly pair users
    usrs = [{'uuid': d['uuid']['S'], 'major': d['major']['S']} for d in usrs]

    # group by majors
    groups = {}

    for user in usrs:
        if user['major'] not in groups:
            groups[user['major']] = []
        groups[user['major']].append(user['uuid'])

    pairs = []
    leftovers = []

    if len(usrs) > 0:
        for users in groups.values():
            for i in range(0, len(users), 2):
                if i == len(users) - 1:
                    leftovers.append(users[i])
                else:
                    pairs.append((users[i], users[i + 1]))
    
    if len(leftovers) > 0:
        for i in range(0, len(leftovers), 2):
            if i == len(leftovers) - 1:
                continue
            else:
                pairs.append((leftovers[i], leftovers[i + 1]))
        
    for pair in pairs:
        print(pair)
    
    if len(pairs) > 0:
        # store to db
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime('%Y-%m-%d')
        print(formatted_date)

        for pair in pairs:
            match = {
                'match_id': {
                    'S': formatted_date + pair[0] + str(pair[1]),
                },
                'review': {
                    'S': 'N/A',
                },
                'user_id1': {
                    'S': pair[0],
                },
                'user_id2': {
                    'S': str(pair[1]),
                },
                'match_date': {
                    'S': formatted_date,
                },
            }
            dynamo_client.put_item(
                TableName='columbia-coffee-chat-matches',
                Item=match,
            )
        
        # SQS
            attr = {}
            attr['user_id1'] = {'StringValue':pair[0], 'DataType': 'String'}
            attr['user_id2'] = {'StringValue':str(pair[1]), 'DataType': 'String'}
            send_message(URL, 'match', attr)

    
    return {
        'statusCode': 200,
        'body': json.dumps('lf6')
    }

def send_message(url, message_body, message_attributes=None):
    """
    Send a message to an Amazon SQS queue.
    :param message_body: The body text of the message.
    :param message_attributes: Custom attributes of the message. These are key-value
                               pairs that can be whatever you want.
    :return: The response from SQS that contains the assigned message ID.
    """
    if not message_attributes:
        message_attributes = {}

    try:
        response = sqs_client.send_message(
            QueueUrl=url,
            MessageBody=message_body,
            MessageAttributes=message_attributes
        )
    except ClientError as error:
        print("Send message failed: %s", message_body)
        raise error
    else:
        return response