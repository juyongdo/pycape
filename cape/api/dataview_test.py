import pytest
from dataview import DataView


class TestDataView:
    def test__repr__(self):
        id = "abc123"
        dv = DataView(id=id)

        assert repr(dv) == f"<{dv.__class__.__name__} ID: {id}>"

    @pytest.mark.parametrize(
        "user_id,owner_id,expectation",
        [("user_1", "user_2", None), ("user_1", "user_1", "s3://my-data.csv"),],
    )
    def test_uri_property(self, user_id, owner_id, expectation):
        dv = DataView(
            name="my-data", user_id=user_id, owner_id=owner_id, uri="s3://my-data.csv"
        )

        assert dv.location == expectation
