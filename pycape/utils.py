import pathlib
from datetime import datetime

import boto3


def filter_date(string: str) -> datetime:
    acceptable_fmts = (
        "%Y",
        "%Y-%m-%d",
        "%b %d, %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%B %d %Y",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%b %Y",
        "%B%Y",
        "%b %d,%Y",
    )

    date = None
    for fmt in acceptable_fmts:
        try:
            date = datetime.strptime(string, fmt)
            break
        except ValueError:
            pass

    return date


def setup_boto_file(uri: pathlib.PosixPath, temp_file_name: str) -> str:
    # tell boto3 we are pulling from s3, p.netloc will be the bucket
    b = boto3.resource(uri.scheme).Bucket(uri.netloc)

    # save the weights for this job in a temp file
    b.download_file(uri.path.lstrip("/"), temp_file_name)

    return temp_file_name


def setup_boto_file_weights(uri: pathlib.PosixPath, temp_file_name: str) -> str:
    # tell boto3 we are pulling from s3, p.netloc will be the bucket
    b = boto3.resource(uri.scheme).Bucket(uri.netloc)

    print(uri.path.lstrip("/") + "/regression_weights.csv")
    # save the weights for this job in a temp file
    b.download_file(uri.path.lstrip("/") + "/regression_weights.csv", temp_file_name)

    return temp_file_name
