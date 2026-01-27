import boto3
import os

class S3Provider:
    def __init__(self, endpoint=None, access_key=None, secret_key=None, bucket=None):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.client = None

    def connect(self):
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

    def upload_file(self, local_path, s3_key):
        if not self.client:
            self.connect()
        self.client.upload_file(local_path, self.bucket, s3_key)

    def download_file(self, s3_key, local_path):
        if not self.client:
            self.connect()
        self.client.download_file(self.bucket, s3_key, local_path)
