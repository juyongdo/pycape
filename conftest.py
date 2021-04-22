import os
import pytest
from moto import mock_s3
import boto3

BUCKET_NAME = "my-data"

@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture(scope="session", autouse=True)
def s3_client(aws_credentials):
    with mock_s3():
        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=BUCKET_NAME)
        yield conn