import contextlib
from io import StringIO

import pytest
import responses

from tests.fake import FAKE_HOST
from tests.fake import fake_dataframe

from ...exceptions import GQLException
from ...network.requester import Requester
from ...vars import JOB_TYPE_LR
from ..dataview.dataview import DataView
from ..job.job import Job
from ..job.vertical_linear_regression_job import VerticalLinearRegressionJob
from ..organization.organization import Organization
from ..project.project import Project


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
        "json,dvs,uri_type,schema,exception",
        [
            (
                {
                    "data": {
                        "addDataView": {
                            "id": "abc123",
                            "name": "my-data",
                            "location": "http://my-data.csv",
                        }
                    }
                },
                [],
                "http",
                None,
                notraising(),
            ),
            (
                {
                    "data": {
                        "addDataView": {
                            "id": "abc123",
                            "name": "my-data",
                            "location": "https://my-data.csv",
                        }
                    }
                },
                [],
                "https",
                None,
                notraising(),
            ),
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
                [
                    {
                        "id": "def123",
                        "name": "my-dataview",
                        "location": "https",
                        "schema": [{"name": "col_1", "schema_type": "string"}],
                        "owner": {
                            "id": "org_123",
                            "label": "my-org",
                            "members": [{"id": "user_123"}],
                        },
                    }
                ],
                "s3",
                [{"name": "col_1", "schema_type": "integer"}],
                notraising(),
            ),
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
                [],
                "s3",
                None,
                pytest.raises(Exception, match="DataView schema must be specified."),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                [],
                "http",
                None,
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_add_dataview(self, json, dvs, uri_type, schema, exception, mocker):
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
                data_views=dvs,
            )
            my_data_view = DataView(
                name="my-data", uri=f"{uri_type}://my-data.csv", schema=schema
            )
            dataview = my_project.add_dataview(dataview=my_data_view)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(dataview, DataView)
            assert len(my_project.dataviews) == len(dvs) + 1
            assert isinstance(my_project.dataviews[len(dvs) - 1], DataView)
            assert dataview.id == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "user_id,json,out_expect,exception",
        [
            (
                "user_123",
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
                                    "owner": {
                                        "id": "org_123",
                                        "label": "my-org",
                                        "members": [{"id": "user_123"}],
                                    },
                                }
                            ],
                        }
                    }
                },
                (
                    "DATAVIEW ID    NAME         LOCATION    OWNER"
                    "\n-------------  -----------  ----------  ------------\n"
                    "def123         my-dataview  https       my-org (You)"
                ),
                notraising(),
            ),
            (
                "user_123",
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
                                    "owner": {
                                        "id": "org_123",
                                        "label": "my-org",
                                        "members": [{"id": "user_123"}],
                                    },
                                },
                                {
                                    "id": "def456",
                                    "name": "your-dataview",
                                    "location": "",
                                    "schema": [
                                        {"name": "col_1", "schema_type": "string"}
                                    ],
                                    "owner": {
                                        "id": "another_org_123",
                                        "label": "your-org",
                                        "members": [{"id": "another_user_123"}],
                                    },
                                },
                            ],
                        }
                    }
                },
                (
                    "DATAVIEW ID    NAME           LOCATION    OWNER"
                    "\n-------------  -------------  ----------  ------------\n"
                    "def123         my-dataview    https       my-org (You)\n"
                    "def456         your-dataview              your-org"
                ),
                notraising(),
            ),
            (
                None,
                {"errors": [{"message": "something went wrong"}]},
                None,
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_list_dataviews(self, user_id, json, out_expect, exception, mocker):
        with exception:
            mocker.patch(
                "cape.api.dataview.dataview.pd.read_csv", return_value=fake_dataframe()
            )
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            out = StringIO()
            my_project = Project(
                requester=r,
                out=out,
                user_id=user_id,
                id="123",
                name="my project",
                label="my project",
            )
            dataviews = my_project.list_dataviews()

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert output == out_expect
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

    @responses.activate
    @pytest.mark.parametrize(
        "id,json,dvs,exception",
        [
            (
                "dv_123",
                {"data": {"removeDataView": {"id": "dv_123"}}},
                [
                    {
                        "id": "dv_123",
                        "name": "my-dataview",
                        "location": "https",
                        "schema": [{"name": "col_1", "schema_type": "string"}],
                        "owner": {
                            "id": "org_123",
                            "label": "my-org",
                            "members": [{"id": "user_123"}],
                        },
                    }
                ],
                notraising(),
            ),
            (
                "dv_123",
                {"errors": [{"message": "something went wrong"}]},
                [],
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_remove_dataview(self, id, json, dvs, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            out = StringIO()
            my_project = Project(
                requester=r,
                out=out,
                user_id=None,
                id="123",
                name="my project",
                label="my-project",
                data_views=dvs,
            )
            my_project.remove_dataview(id=id)

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert isinstance(output, str)
            assert output == "DataView (dv_123) deleted"
            assert len(my_project.dataviews) == len(dvs) - 1

    @responses.activate
    def test_approve_job(self):
        responses.add(
            responses.POST,
            f"{FAKE_HOST}/v1/query",
            json={
                "data": {
                    "approveJob": {
                        "id": "abc123",
                        "status": {"code": "Initialized"},
                        "task": {"type": JOB_TYPE_LR},
                    }
                }
            },
        )
        r = Requester(endpoint=FAKE_HOST)
        my_project = Project(
            requester=r, user_id=None, id="123", name="my project", label="my-project",
        )
        org = Organization(id="org123")
        j = Job(id="abc123", job_type=JOB_TYPE_LR, requester=r)
        my_project.approve_job(j, org)
