import contextlib
import os

import pytest
from moto import mock_s3
import boto3
import tempfile
from urllib.parse import urlparse
from tests.fake import fake_csv_dob_date_field
from tests.fake import fake_dataframe

from .dataview import DataView

bucket_name = "my-data"


@contextlib.contextmanager
def notraising():
    yield


@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture(scope="session", autouse=True)
def s3_client(aws_credentials):
    with mock_s3():
        conn = boto3.resource("s3", region_name="us-east-1")
        conn.create_bucket(Bucket=bucket_name)
        yield conn


class TestDataView:
    def test__repr__(self):
        id = "abc123"
        name = "hey"
        location = "cool.com"
        dv = DataView(id=id, name=name, location=location)

        expect = f"{dv.__class__.__name__}(id={id}, name={name}, location={location})"
        assert repr(dv) == expect

    def test__get_item__(self):
        dv_1 = DataView(name="my-data", location="s3://my-data.csv")
        dv_with_col = dv_1["col_1"]

        dv_2 = DataView(name="my-data", location="s3://my-data.csv")
        dv_with_cols = dv_2["col_1", "col_2"]

        assert isinstance(dv_with_col, DataView)
        assert dv_with_col._cols == ["col_1"]

        assert isinstance(dv_with_cols, DataView)
        assert dv_with_cols._cols == ["col_1", "col_2"]

    @pytest.mark.parametrize(
        "schema,expectation,exception",
        [
            (None, type(None), notraising()),
            (fake_dataframe().dtypes, list, notraising()),
            ([{"name": "col_1", "schema_type": "string"}], list, notraising()),
            (
                fake_dataframe()["col1"],
                None,
                pytest.raises(Exception, match="Invalid schema*"),
            ),
            (
                [{"name": "col_1", "type": "string"}],
                None,
                pytest.raises(Exception, match="Invalid schema*"),
            ),
            (True, None, pytest.raises(Exception, match="Schema is not of type*")),
            (
                fake_dataframe(),
                None,
                pytest.raises(Exception, match="Schema is not of type*"),
            ),
        ],
    )
    def test_validate_schema(self, schema, expectation, exception):
        with exception:
            parse_schema = DataView._validate_schema(schema=schema)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(parse_schema, expectation)

    @pytest.mark.parametrize(
        "uri,side_effect,exception",
        [
            ("http://my-data.csv", None, notraising()),
            (f"s3://{bucket_name}/123/data.csv", None, notraising()),
            (
                "http://my-data.csv",
                FileNotFoundError,
                pytest.raises(
                    Exception,
                    match="Resource not accessible, please specify the data's schema.",
                ),
            ),
        ],
    )
    def test_get_schema_from_uri(
        self, uri, side_effect, exception, mocker, s3_client,
    ):
        with exception:
            mocker.patch(
                "pycape.api.dataview.dataview.pd.read_csv",
                side_effect=side_effect,
                return_value=fake_csv_dob_date_field(),
            )
            if urlparse(uri).scheme == "s3":
                tf = tempfile.NamedTemporaryFile(suffix=".csv")
                boto3.resource("s3").Bucket(bucket_name).upload_file(
                    tf.name, urlparse(uri).path.lstrip("/")
                )

            schema = DataView._get_schema_from_uri(uri=uri)

            if isinstance(exception, contextlib._GeneratorContextManager):
                assert [s for s in schema if s.get("name") == "dob"][0].get(
                    "schema_type"
                ) == "datetime"
