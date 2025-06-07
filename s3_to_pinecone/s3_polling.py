import io
import json
import time
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from data_insertion import insert_vectordatabase
import os
from dotenv import load_dotenv
load_dotenv()
# AWS config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
REGION = "us-east-1"
QUEUE_URL = os.getenv("QUEUE_URL")

# Create clients
sqs = boto3.client('sqs', region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY)

s3 = boto3.client('s3', region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY)

def listen_to_sqs():
    print("Listening to SQS every 10 minutes...")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                AttributeNames=['All'],
                MaxNumberOfMessages=1,
                MessageAttributeNames=['All'],
                VisibilityTimeout=300,  # 5 minutes
                WaitTimeSeconds=20     # Long polling
            )

            if 'Messages' in response:
                message = response['Messages'][0]
                receipt_handle = message['ReceiptHandle']

                try:
                    body = json.loads(message['Body'])
                    record = body['Records'][0]
                    s3_key = record['s3']['object']['key']
                    s3_bucket = record['s3']['bucket']['name']

                    print(f"Received S3 event: s3://{s3_bucket}/{s3_key}")

                    # Download CSV from S3
                    temp_file = io.BytesIO()
                    s3.download_fileobj(s3_bucket, s3_key, temp_file)
                    temp_file.seek(0)

                    # Process and insert into Pinecone
                    print("now inserting into pinecone")
                    try:
                       insert_vectordatabase(temp_file)
                       sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
                       print("Message processed and deleted from queue.")
                    except Exception as e:
                       print("Failed to insert into Pinecone:", str(e))

                except Exception as e:
                    print(f"Error processing message: {e}")

            else:
                print("No messages...")

        except (BotoCoreError, ClientError) as error:
            print("AWS error:", error)

        # Wait 10 minutes before polling again
        time.sleep(600)

if __name__ == "__main__":
    listen_to_sqs()
