import contextlib

import pytest
import responses

from .dataview import DataView
from tests.fake import fake_csv_dob_date_field, fake_dataframe


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
        dv_1 = DataView(name="my-data", uri="s3://my-data.csv")
        dv_with_col = dv_1["col_1"]

        dv_2 = DataView(name="my-data", uri="s3://my-data.csv")
        dv_with_cols = dv_2["col_1", "col_2"]

        assert isinstance(dv_with_col, DataView)
        assert dv_with_col._cols == ["col_1"]

        assert isinstance(dv_with_cols, DataView)
        assert dv_with_cols._cols == ["col_1", "col_2"]

    @responses.activate
    @pytest.mark.parametrize(
        "owner_id,user_id,expectation",
        [("main_user", "main_user", "s3://my-data.csv")],
    )
    def test_location_property(self, owner_id, user_id, expectation, mocker):
        dv = DataView(
            name="my-data", uri="s3://my-data.csv", owner_id=owner_id, user_id=user_id
        )

        assert dv.location == expectation

    @pytest.mark.parametrize(
        "schema,expectation,exception",
        [
            (None, type(None), notraising()),
            (fake_dataframe().dtypes, dict, notraising()),
            ([{"name": "col_1", "schema_type": "string"}], dict, notraising()),
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
    def test_schema_property(self, schema, expectation, exception):
        with exception:
            dv = DataView(name="my-data", schema=schema, uri="s3://my-data.csv")

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dv.schema, expectation)

    @pytest.mark.parametrize(
        "side_effect,exception",
        [
            (None, notraising()),
            (
                FileNotFoundError,
                pytest.raises(Exception, match="Cannot access data resourc"),
            ),
        ],
    )
    def test_get_schema_from_uri(self, side_effect, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv",
                side_effect=side_effect,
                return_value=fake_csv_dob_date_field(),
            )
            dv = DataView(name="my-data", uri="s3://my-data.csv")
            schema = dv._get_schema_from_uri()

            if isinstance(exception, contextlib._GeneratorContextManager):
                assert [s for s in schema if s.get("name") == "dob"][0].get(
                    "schema_type"
                ) == "datetime"
