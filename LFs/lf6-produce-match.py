import boto3
from botocore.exceptions import ClientError
import json
import random
import datetime
import inflection


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
    usrs = [{
        'uuid': inflection.singularize(d['uuid']['S']).lower(),
        'major': inflection.singularize(d['major']['S']).lower(),
        'school_year': inflection.singularize(d['school_year']['S']).lower(),
        'program': inflection.singularize(d['program']['S']).lower(),
        'classes': [inflection.singularize(c['S']).lower() for i, c in enumerate(d['classes']['L']) if i < 5],
        'interests': [inflection.singularize(c['S']).lower() for i, c in enumerate(d['interests']['L']) if i < 5],
        'match_pref': d['major_pref']['S']
    } for d in usrs]

    users_same = [user for user in usrs if user['match_pref'] == 'same']
    users_diff = [user for user in usrs if user['match_pref'] == 'different']

    pairs = []
    leftovers = users_diff
    matched = set()

    # groups
    groups = {}
    majors = []
    school_years = []
    programs = []
    classes = []
    interests = []

    for user in users_same:
        if user['major'] not in groups:
            majors.append(user['major'])
            groups[user['major']] = []
        groups[user['major']].append(user['uuid'])

        if user['school_year'] not in groups:
            school_years.append(user['school_year'])
            groups[user['school_year']] = []
        groups[user['school_year']].append(user['uuid'])

        if user['program'] not in groups:
            programs.append(user['program'])
            groups[user['program']] = []
        groups[user['program']].append(user['uuid'])

        for cls in user['classes']:
            if cls not in groups:
                classes.append(cls)
                groups[cls] = []
            groups[cls].append(user['uuid'])

        for interest in user['interests']:
            if interest not in groups:
                interests.append(interest)
                groups[interest] = []
            groups[interest].append(user['uuid'])

    keys = majors + classes + interests + school_years + programs

    held_user = None
    maybe_leftovers = []
    for cluster in keys:
        for i, user in enumerate(groups[cluster]):
            if user not in matched and user != held_user:
                if held_user is not None:
                    pairs.append((held_user, user))
                    matched.add(held_user)
                    matched.add(user)
                    held_user = None
                else:
                    held_user = user
            if i == len(groups[cluster]) - 1 and held_user is not None:
                maybe_leftovers.append(held_user)
                held_user = None

    for user in maybe_leftovers:
        if user not in matched:
            leftovers.append(user)
            matched.add(user)

    if len(leftovers) > 0:
        for i in range(0, len(leftovers), 2):
            if i == len(leftovers) - 1:
                pairs.append((leftovers[i], None))
            else:
                pairs.append((leftovers[i], leftovers[i + 1]))
    
    # for pair in pairs:
    #     print(pair)
    
    if len(pairs) > 0:
        for pair in pairs:
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