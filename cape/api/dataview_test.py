from dataview import DataView


class TestDataView:
    def test__repr__(self):
        id = "abc123"
        dv = DataView(id=id)

        assert repr(dv) == f"<{dv.__class__.__name__} ID: {id}>"
