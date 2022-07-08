"""
lambda function gets current pi cases from database and send them to sqs.
"""
import os
import logging
import json
from get_data import create_month_end
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    """
    gets current pi cases from database and send them to sqs.
    """

    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    print("Lambda function memory limits in MB:",context.memory_limit_in_mb)


    result=create_month_end()


    client = boto3.client('sqs',region_name='us-west-2',
    endpoint_url='https://sqs.us-west-2.amazonaws.com')
    queueInfo = client.get_queue_url(QueueName='MonthEnd')
    for clinic in result:
        message=result[clinic]
        message['clinic']=clinic
        messageJson=json.dumps(message)
        client.send_message(
                            QueueUrl = queueInfo['QueueUrl'],
                            MessageBody=messageJson
                        )

    print(result)
    return True
