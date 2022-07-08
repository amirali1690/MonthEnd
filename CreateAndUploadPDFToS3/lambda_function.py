"""
lambda function gets current pi cases from database and send them to sqs.
"""
import os
import logging
import ast
import boto3
from fpdf import FPDF

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    """
    get MonthEnd stats from SQS to create pdf and upload to S3
    """

    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    print("Lambda function memory limits in MB:",context.memory_limit_in_mb)

    pdf=FPDF()
    pdf.add_page()
    client = boto3.client('sqs',region_name='us-west-2')
    responses = client.receive_message(
                    QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/MonthEnd',
                    AttributeNames=['All'],
                    MaxNumberOfMessages = 10
                    )
    counter=0
    while 'Messages' in responses.keys() and (len(responses['Messages']))>0 and counter<10:
        for message in responses['Messages']:
            data=ast.literal_eval(message['Body'])
            print(data,data.keys())
        counter+=1
    return True
