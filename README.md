[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amirali1690/MonthEnd/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/amirali1690/MonthEnd/tree/master)



# PiBalanceUpdate

## Description
The project is a complete CI/CD pipelines of a serverless microservices that creates monthly reports.
An AWS Lambda functions read the data from AWS RDS MySQL Database and send the data to an SQS queue. The SQS queue is polled by another Lambda functions that use the data to create multiple PDF reports and upload them to S3. Then a Presigned URL is created for each PDF and is sent to users via a SNS.

## Tools

* aws-cli
* AWS Lambda
* AWS CloudFormation
* AWS RDS
* AWS SQS
* AWS S3
* CircleCI
* Python packages:
  * pymysql
  * boto3
  
## Prerequisites
* AWS Account
* CircleCI Account
* AWS SNS with required subcribers. 

## Installation
Once you have your AWS and CircleCI account setup, fork the project to your own Github account and connect it to your CircleCI account. 
You need add your AWS credentials(keys) to your CircleCI environment.
Once everything is set, just need to push the code, and it will deploy all services on the AWS via CloudFormation template.


## Contact
If you have any questions or suggestions please contact me on Amirali1690@gmail.com

# MonthEnd  
This project include following parts:  
1- A Lambda function that with Python that run every month and collect data from an AWS RDS MySQL database and upload it to a SQS queue  
2- A Lambda function with Python that read the data from SQS and create a pdf and store in S3. Create a Presigned URL and send the URL to a SNS topic  
3- A SQS Queue that decouple the two Lambda functions  


# Included files  
1- Cloudformation Template(Including Lambda Functions and SQS Queue and required IAM Roles)  
2- CircleCI file  
3- Python codes for Lambda functions  
