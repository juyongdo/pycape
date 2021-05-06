import contextlib
import tempfile
from urllib.parse import urlparse

import boto3
import numpy as np
import pandas as pd
import pytest

from conftest import BUCKET_NAME
from tests.fake import FAKE_COLUMNS
from tests.fake import fake_csv_dob_date_field
from tests.fake import fake_dataframe

from ...exceptions import StorageAccessException
from .dataview import DataView


@contextlib.contextmanager
def notraising():
    yield


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
        "uri,side_effect,data,cols,exception",
        [
            (
                f"s3://{BUCKET_NAME}/123/data.csv",
                None,
                np.array(
                    [[1.0, 22, "alice", "2006-01-13"], [3.0, 21, "bob", "2006-01-13"]]
                ),
                FAKE_COLUMNS,
                notraising(),
            ),
            (
                "s3://my-data/fsdf/df.csv",
                ValueError,
                None,
                None,
                pytest.raises(
                    StorageAccessException, match="Resource not accessible.",
                ),
            ),
        ],
    )
    def test_get_schema_from_uri(
        self, uri, side_effect, data, cols, exception, mocker, s3_client,
    ):
        with exception:
            tf = tempfile.NamedTemporaryFile(suffix=".csv")
            b = boto3.resource("s3").Bucket(BUCKET_NAME)
            pd.DataFrame(data, columns=cols).to_csv(tf.name, header=True)
            b.upload_file(tf.name, urlparse(uri).path.lstrip("/"))

            mocker.patch(
                "pycape.api.dataview.dataview.pd.read_csv",
                side_effect=side_effect,
                return_value=fake_csv_dob_date_field(),
            )
            schema = DataView._get_schema_from_uri(uri=uri)

            if isinstance(exception, contextlib._GeneratorContextManager):
                assert len(schema) == 4
                assert [s for s in schema if s.get("name") == "first_name"][0].get(
                    "schema_type"
                ) == "string"
                assert [s for s in schema if s.get("name") == "height"][0].get(
                    "schema_type"
                ) == "number"
                assert [s for s in schema if s.get("name") == "dob"][0].get(
                    "schema_type"
                ) == "datetime"
                assert [s for s in schema if s.get("name") == "age"][0].get(
                    "schema_type"
                ) == "integer"
