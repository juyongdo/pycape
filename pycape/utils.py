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


def setup_boto_file(
    uri: pathlib.PosixPath, temp_file_name: str, download_path: str = None
) -> str:
    if not download_path:
        download_path = uri.path.lstrip("/")
    # tell boto3 we are pulling from s3, p.netloc will be the bucket
    b = boto3.resource(uri.scheme).Bucket(uri.netloc)

    b.download_file(download_path, temp_file_name)

    return temp_file_name
