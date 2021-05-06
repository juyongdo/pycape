import pathlib
from datetime import datetime
from urllib.parse import urlparse

import boto3
import re

from .exceptions import StorageException, StorageSchemeException


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


def validate_s3_location(uri: str):
    p = urlparse(uri)
    # check bucket for special characters beyond
    # periods and dashes, which are permitted.
    regexp = re.compile("[^0-9a-zA-Z-.]+")

    if not p.netloc or regexp.search(p.netloc):
        raise StorageException(uri=uri)
    elif p.scheme != "s3":
        raise StorageSchemeException(scheme=p.scheme)

    return uri
