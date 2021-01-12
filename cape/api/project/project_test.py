import pytest
import responses
import contextlib

from cape.network.requester import Requester
from cape.api.dataview.dataview import DataView
from cape.api.project.project import Project
from cape.exceptions import GQLException
from tests.fake import fake_dataframe, FAKE_HOST


@contextlib.contextmanager
def notraising():
    yield


class TestProject:
    def test__repr__(self):
        id = "abc123"
        name = "my project"
        label = "my-project"
        p = Project(requester=None, id=id, name=name, label=label)

        assert (
            repr(p) == f"<{p.__class__.__name__} (id={id}, name={name}, label={label})>"
        )

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "addDataView": {
                            "id": "abc123",
                            "name": "my-data",
                            "location": "s3://my-data.csv",
                        }
                    }
                },
                notraising(),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_add_dataview(self, json, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv", return_value=fake_dataframe()
            )
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_project = Project(
                requester=r, id="123", name="my project", label="my project"
            )
            dataview = my_project.add_dataview(name="my-data", uri="s3://my-data.csv")

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dataview, DataView)
            assert dataview.id == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "project": {
                            "id": "abc123",
                            "label": "my-project",
                            "data_views": [
                                {
                                    "id": "def123",
                                    "name": "my-dataview",
                                    "location": "https",
                                    "schema": [
                                        {"name": "col_1", "schema_type": "string"}
                                    ],
                                }
                            ],
                        }
                    }
                },
                notraising(),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_list_dataviews(self, json, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv", return_value=fake_dataframe()
            )
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_project = Project(
                requester=r, id="123", name="my project", label="my project"
            )

            dataviews = my_project.list_dataviews()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dataviews, list)
            assert dataviews[0].id == "def123"
            assert isinstance(dataviews[0].schema, dict)
            assert dataviews[0].schema["col_1"] == "string"

    @responses.activate
    @pytest.mark.parametrize(
        "args,json,exception",
        [
            (
                {"id": "dataview_123"},
                {
                    "data": {
                        "project": {
                            "id": "project_123",
                            "label": "my-project",
                            "data_views": [
                                {
                                    "id": "dataview_123",
                                    "name": "my-dataview",
                                    "location": "https",
                                    "schema": [
                                        {"name": "col_1", "schema_type": "string"}
                                    ],
                                }
                            ],
                        }
                    }
                },
                notraising(),
            ),
            (
                {"uri": "https"},
                {
                    "data": {
                        "project": {
                            "id": "project_123",
                            "label": "my-project",
                            "data_views": [
                                {
                                    "id": "dataview_123",
                                    "name": "my-dataview",
                                    "location": "https",
                                    "schema": [
                                        {"name": "col_1", "schema_type": "string"}
                                    ],
                                }
                            ],
                        }
                    }
                },
                notraising(),
            ),
            (
                {"id": "dataview_123"},
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
            (
                {},
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(Exception, match="Required identifier*"),
            ),
        ],
    )
    def test_get_dataview(self, args, json, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv", return_value=fake_dataframe()
            )
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_project = Project(
                requester=r, id="123", name="my project", label="my project"
            )
            dataviews = my_project.get_dataview(**args)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dataviews, DataView)
            assert dataviews.id == "dataview_123"
            assert isinstance(dataviews.schema, dict)
            assert dataviews.schema["col_1"] == "string"
