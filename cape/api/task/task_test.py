from ..dataview.dataview import DataView
from .vertical_linear_regression_task import VerticallyPartitionedLinearRegression
from .task import Task


class TestTask:
    def test_task__repr__(self):
        id = "abc123"

        t = Task(id=id)
        rep = f"Task(id={id})"

        assert repr(t) == rep

    def test_job__repr__(self):
        dataview_x = DataView(
            id="dv_x",
            name="my-data-x",
            location="s3://my-data.csv",
            schema=[{"name": "a", "schema_type": "string"}],
        )
        dataview_y = DataView(
            id="dv_y",
            name="my-data-y",
            location="s3://my-data.csv",
            schema=[{"name": "b", "schema_type": "string"}],
        )
        t = VerticallyPartitionedLinearRegression(
            x_train_dataview=dataview_x, y_train_dataview=dataview_y["b"],
        )
        rep = "VerticallyPartitionedLinearRegression(x_train_dataview=my-data-x, y_train_dataview=my-data-y['b'])"

        assert repr(t) == rep
