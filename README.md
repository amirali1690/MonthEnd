# MonthEnd
This project include following parts:
1- A Lambda function that with Python that run every month and collect data from an AWS RDS MySQL database and upload it to a SQS queue
2- A Lambda function with Python that read the data from SQS and create a pdf and store in S3. Create a Presigned URL and send the URL to a SNS topic
3- A SQS Queue that decouple the two Lambda functions


# Included files
1- Cloudformation Template(Including Lambda Functions and SQS Queue and required IAM Roles)
2- CircleCI file
3- Python codes for Lambda functions
