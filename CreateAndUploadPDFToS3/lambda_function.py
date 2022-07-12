"""
lambda function gets current pi cases from database and send them to sqs.
"""
import os
import logging
import ast
import boto3
from functions import create_pdf,create_presigned_url,send_to_sns

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

    s3Resource = boto3.resource('s3')
    client = boto3.client('sqs',region_name='us-west-2')
    responses = client.receive_message(
                    QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/MonthEnd',
                    AttributeNames=['All'],
                    MaxNumberOfMessages = 10
                    )
    counter=0
    urls={}
    while 'Messages' in responses.keys() and (len(responses['Messages']))>0 and counter<10:
        for message in responses['Messages']:
            data=ast.literal_eval(message['Body'])
            create_pdf(data)
            s3Resource.meta.client.upload_file('/tmp/'+data['month']+'-'+data['clinic']+'.pdf',
                            'monthly-report-bfh',data['month']+'/'+data['clinic']+'.pdf')
            urls[data['clinic']]=create_presigned_url('monthly-report-bfh', data['month']+
                '/'+data['clinic']+'.pdf', expiration=604800)
        counter+=1
        responses = client.receive_message(
                QueueUrl = 'https://sqs.us-west-2.amazonaws.com/849779278892/MonthEnd',
                AttributeNames=['All'],
                MaxNumberOfMessages = 10
                )
    for clinic,message in urls.items():
        send_to_sns(clinic,message)
    return True
