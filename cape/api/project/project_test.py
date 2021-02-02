import contextlib

import pytest
import responses
from io import StringIO

from cape.api.dataview.dataview import DataView
from cape.api.project.project import Project
from cape.api.job.vertical_linear_regression_job import VerticalLinearRegressionJob
from cape.exceptions import GQLException
from cape.network.requester import Requester
from cape.vars import JOB_TYPE_LR
from tests.fake import FAKE_HOST
from tests.fake import fake_dataframe


@contextlib.contextmanager
def notraising():
    yield


class TestProject:
    def test__repr__(self):
        id = "abc123"
        name = "my project"
        label = "my-project"
        p = Project(requester=None, user_id=None, id=id, name=name, label=label)

        assert repr(p) == f"{p.__class__.__name__}(id={id}, name={name}, label={label})"

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
                requester=r,
                user_id=None,
                id="123",
                name="my project",
                label="my project",
            )
            my_data_view = DataView(name="my-data", uri="s3://my-data.csv")
            dataview = my_project.add_dataview(dataview=my_data_view)

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
                requester=r,
                user_id=None,
                id="123",
                name="my project",
                label="my project",
            )
            out = StringIO()
            my_project.list_dataviews(out=out)

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert output == (
                "DATAVIEW ID    NAME         LOCATION    SCHEMA"
                "\n-------------  -----------  ----------  -------------------\n"
                "def123         my-dataview              {'col_1': 'string'}"
            )

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
                requester=r,
                user_id=None,
                id="123",
                name="my project",
                label="my project",
            )
            dataviews = my_project.get_dataview(**args)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dataviews, DataView)
            assert dataviews.id == "dataview_123"
            assert isinstance(dataviews.schema, dict)
            assert dataviews.schema["col_1"] == "string"

    @responses.activate
    @pytest.mark.parametrize(
        "id,json,exception",
        [
            (
                "job_123",
                {
                    "data": {
                        "project": {
                            "job": {
                                "id": "job_123",
                                "status": {"code": "Initialized"},
                                "task": {"type": JOB_TYPE_LR},
                            }
                        }
                    }
                },
                notraising(),
            ),
            (
                "job_123",
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_get_job(self, id, json, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv", return_value=fake_dataframe()
            )
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_project = Project(
                requester=r,
                user_id=None,
                id="123",
                name="my project",
                label="my-project",
            )
            job = my_project.get_job(id=id)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(job, VerticalLinearRegressionJob)
            assert job.id == id
            assert job.status == {"code": "Initialized"}
