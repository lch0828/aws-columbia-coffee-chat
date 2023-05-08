import boto3
from botocore.exceptions import ClientError
import json


queue = boto3.client('sqs')
URL = 'https://sqs.us-east-1.amazonaws.com/094343250950/match-email'
dynamo_client = boto3.client('dynamodb')

def lambda_handler(event, context):
    msgs = receive_messages(queue, URL)

    if 'Messages' in msgs:
        for msg in msgs['Messages']:
            usr1_id = msg['MessageAttributes']['user_id1']['StringValue']
            usr2_id = msg['MessageAttributes']['user_id2']['StringValue']
            print(usr1_id, usr2_id)
            if usr2_id != 'None':
                usr1_info = dynamo_client.get_item(
                  TableName='columbia-coffee-chat-users',
                  Key={'uuid':{'S':str(usr1_id)}}
                )
                usr2_info = dynamo_client.get_item(
                  TableName='columbia-coffee-chat-users',
                  Key={'uuid':{'S':str(usr2_id)}}
                )

                usr1_email = usr1_info['Item']['email']['S']
                usr2_email = usr2_info['Item']['email']['S']
                
                message_to_usr1 = f"Matched with {usr2_info['Item']['fname']['S']} {usr2_info['Item']['lname']['S']}"
                message_to_usr2 = f"Matched with {usr1_info['Item']['fname']['S']} {usr1_info['Item']['lname']['S']}"
                
                send_email(usr1_email, message_to_usr1)
                send_email(usr2_email, message_to_usr2)
            else:
                usr1_info = dynamo_client.get_item(
                  TableName='columbia-coffee-chat-users',
                  Key={'uuid':{'S':str(usr1_id)}}
                )
                
                usr1_email = usr1_info['Item']['email']['S']
                
                print(usr1_email)
                
                message_to_usr1 = f'No match for you :('
                 
                send_email(usr1_email, message_to_usr1)

    return {
        'statusCode': 200,
        'body': json.dumps('lf9')
    }
    
def receive_messages(queue, url, max_number=10, wait_time=10):
    """
    Receive a batch of messages in a single request from an SQS queue.
    :param queue: The queue from which to receive messages.
    :param max_number: The maximum number of messages to receive. The actual number
                       of messages received might be less.
    :param wait_time: The maximum time to wait (in seconds) before returning. When
                      this number is greater than zero, long polling is used. This
                      can result in reduced costs and fewer false empty responses.
    :return: The list of Message objects received. These each contain the body
             of the message and metadata and custom attributes.
    """
    try:
        messages = queue.receive_message(
            QueueUrl=url,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time
        )
        print('messages: ', messages)
    except ClientError as error:
        print("Couldn't receive messages from queue: %s", queue)
        raise error
    else:
        if "Messages" in messages:
            response = queue.delete_message(
                QueueUrl=url,
                ReceiptHandle=messages['Messages'][0]['ReceiptHandle']
            )
        return messages
        
def send_email(mail, message):
    SENDER = "mjbl8228@gmail.com" # this is ben's email
    RECIPIENT = mail
    AWS_REGION = "us-east-1"
    SUBJECT = "Match Info"
    BODY_TEXT = message
    CHARSET = "UTF-8"
    
    client = boto3.client('ses',region_name=AWS_REGION)
    
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
