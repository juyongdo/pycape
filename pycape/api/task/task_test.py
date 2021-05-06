import contextlib

import pytest

from ...exceptions import StorageSchemeException, StorageException
from ..dataview.dataview import DataView
from .task import Task
from .vertical_linear_regression_task import VerticallyPartitionedLinearRegression


@contextlib.contextmanager
def notraising():
    yield


class TestTask:
    def test_task__repr__(self):
        id = "abc123"
        model_location = "s3://my-bucket"
        model_owner = "org123"
        t = Task(id=id, model_location=model_location, model_owner=model_owner)
        rep = f"Task(id={id}, model_owner={model_owner})"

        assert repr(t) == rep

    def test_vplr__repr__(self):
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
            x_train_dataview=dataview_x,
            y_train_dataview=dataview_y["b"],
            model_location="s3://my-location",
            model_owner="org123",
        )
        rep = (
            "VerticallyPartitionedLinearRegression(x_train_dataview=my-data-x, y_train_dataview=my-data-y['b'], "
            "model_location=s3://my-location, model_owner=org123)"
        )

        assert repr(t) == rep

    @pytest.mark.parametrize(
        "model_location,exception",
        [
            ("s3://my-location", notraising()),
            ("s3://my.location", notraising()),
            ("s3://mylocation123", notraising()),
            (
                "not a uri",
                pytest.raises(
                    StorageException, match="Invalid s3 bucket provided: not a uri"
                ),
            ),
            (
                "file://bucket",
                pytest.raises(
                    StorageSchemeException, match="Only s3 locations supported, got"
                ),
            ),
            (
                "s3://s3://bucket",
                pytest.raises(
                    StorageException,
                    match="Invalid s3 bucket provided: s3://s3://bucket",
                ),
            ),
            (None, pytest.raises(Exception, match="no model location provided")),
        ],
    )
    def test_model_location(self, model_location, exception):
        with exception:
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
                x_train_dataview=dataview_x,
                y_train_dataview=dataview_y["b"],
                model_location=model_location,
                model_owner="org123",
            )

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert t.model_location == model_location

    @pytest.mark.parametrize(
        "model_owner,exception",
        [
            ("org123", notraising()),
            (None, pytest.raises(Exception, match="no model owner provided")),
        ],
    )
    def test_model_owner(self, model_owner, exception):
        with exception:
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
                x_train_dataview=dataview_x,
                y_train_dataview=dataview_y["b"],
                model_location="s3://my-location",
                model_owner=model_owner,
            )

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert t.model_owner == model_owner

    @pytest.mark.parametrize(
        "x_dataview,y_dataview,exception",
        [
            (
                DataView(
                    id="dv_x",
                    name="my-data-x",
                    location="s3://my-data.csv",
                    schema=[{"name": "a", "schema_type": "string"}],
                ),
                DataView(
                    id="dv_y",
                    name="my-data-y",
                    location="s3://my-data.csv",
                    schema=[{"name": "b", "schema_type": "string"}],
                ),
                notraising(),
            ),
            (
                DataView(
                    name="my-data-x",
                    location="s3://my-data.csv",
                    schema=[{"name": "a", "schema_type": "string"}],
                ),
                DataView(
                    id="dv_y",
                    name="my-data-y",
                    location="s3://my-data.csv",
                    schema=[{"name": "b", "schema_type": "string"}],
                ),
                pytest.raises(
                    Exception, match="DataView Missing Properties: x DataView ID"
                ),
            ),
            (
                None,
                DataView(
                    id="dv_y",
                    name="my-data-y",
                    location="s3://my-data.csv",
                    schema=[{"name": "b", "schema_type": "string"}],
                ),
                pytest.raises(Exception, match="x DataView missing"),
            ),
            (
                DataView(
                    id="dv_x",
                    name="my-data-x",
                    location="s3://my-data.csv",
                    schema=[{"name": "a", "schema_type": "string"}],
                ),
                DataView(
                    name="my-data-y",
                    location="s3://my-data.csv",
                    schema=[{"name": "b", "schema_type": "string"}],
                ),
                pytest.raises(
                    Exception, match="DataView Missing Properties: y DataView ID"
                ),
            ),
            (
                DataView(
                    id="dv_x",
                    name="my-data-x",
                    location="s3://my-data.csv",
                    schema=[{"name": "a", "schema_type": "string"}],
                ),
                None,
                pytest.raises(Exception, match="y DataView missing"),
            ),
            (
                DataView(id="dv_x", name="my-data-x", location="s3://my-data.csv",),
                DataView(
                    id="dv_y",
                    name="my-data-y",
                    location="s3://my-data.csv",
                    schema=[{"name": "b", "schema_type": "string"}],
                ),
                pytest.raises(
                    Exception, match="DataView Missing Properties: x DataView columns"
                ),
            ),
        ],
    )
    def test_train_dataview_params(self, x_dataview, y_dataview, exception):
        with exception:
            t = VerticallyPartitionedLinearRegression(
                x_train_dataview=x_dataview,
                y_train_dataview=y_dataview,
                model_location="s3://my-location",
                model_owner="org123",
            )
            t.x_train_dataview = x_dataview
            t.y_train_dataview = y_dataview

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert t.x_train_dataview == x_dataview
            assert t.y_train_dataview == y_dataview
