import contextlib

import pytest
import responses

from tests.fake import FAKE_HOST

from ...network.requester import Requester
from ...vars import JOB_TYPE_LR
from ..dataview.dataview import DataView
from ..project.project import Project
from ..task.vertical_linear_regression_task import VerticallyPartitionedLinearRegression
from .job import Job


@contextlib.contextmanager
def notraising():
    yield


class TestJob:
    def test__repr__(self):
        id = "abc123"

        r = Requester(endpoint=FAKE_HOST)
        j = Job(
            id=id,
            task={"type": JOB_TYPE_LR},
            status={"code": "Initialized"},
            requester=r,
            project_id="p_123",
        )
        rep = f"Job(id={id}, job_type={JOB_TYPE_LR}, status=Initialized)"

        assert repr(j) == rep

    @responses.activate
    @pytest.mark.parametrize(
        "json,dataview_x,dataview_y,dataview_col_x,dataview_col_y,exception",
        [
            (
                {
                    "data": {
                        "initializeSession": {
                            "id": "session_123",
                            "status": {"code": "Initialized"},
                            "task": {"type": "LINEAR_REGRESSION"},
                        }
                    }
                },
                DataView(id="dv_1", name="my-data", location="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", location="s3://my-data-2.csv"),
                "123",
                "123",
                notraising(),
            ),
            (
                {
                    "data": {
                        "initializeSession": {
                            "id": "session_123",
                            "status": {"code": "Initialized"},
                            "task": {"type": "LINEAR_REGRESSION"},
                        }
                    }
                },
                DataView(name="my-data", location="s3://my-data.csv"),
                DataView(name="my-data_1", location="s3://my-data-2.csv"),
                "123",
                "123",
                pytest.raises(
                    Exception,
                    match="DataView Missing Properties: X DataView ID, Y DataView ID",
                ),
            ),
            (
                {
                    "data": {
                        "initializeSession": {
                            "id": "session_123",
                            "status": {"code": "Initialized"},
                            "task": {"type": "LINEAR_REGRESSION"},
                        }
                    }
                },
                DataView(id="dv_1", name="my-data", location="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", location="s3://my-data-2.csv"),
                None,
                None,
                pytest.raises(
                    Exception,
                    match="DataView Missing Properties: X DataView columns, Y DataView columns",
                ),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                DataView(id="dv_1", name="my-data", location="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", location="s3://my-data-2.csv"),
                "123",
                "123",
                pytest.raises(Exception, match="An error occurred: .*"),
            ),
            (
                {
                    "data": {
                        "initializeSession": {
                            "id": "session_123",
                            "status": {"code": "Initialized"},
                            "task": {"type": "LINEAR_REGRESSION"},
                        }
                    }
                },
                DataView(
                    id="dv_1",
                    name="my-data",
                    location="s3://my-data.csv",
                    schema=[{"name": "123", "schema_type": "string"}],
                ),
                DataView(
                    id="dv_2",
                    name="my-data_1",
                    location="s3://my-data-2.csv",
                    schema=[{"name": "123", "schema_type": "string"}],
                ),
                None,
                None,
                notraising(),
            ),
        ],
    )
    def test_submit_lr_job(
        self,
        json,
        dataview_x,
        dataview_y,
        dataview_col_x,
        dataview_col_y,
        exception,
        mocker,
    ):
        with exception:
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

            task_config = {
                "x_train_dataview": dataview_x[dataview_col_x],
                "y_train_dataview": dataview_y[dataview_col_y],
            }
            vlr = VerticallyPartitionedLinearRegression(**task_config)

            submitted_job = my_project.submit_job(vlr)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(submitted_job, Job)
            assert submitted_job.id == "session_123"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "project": {
                            "job": {"id": "abc_123", "status": {"code": "Initialized"}}
                        }
                    }
                },
                notraising(),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(Exception, match="An error occurred: .*"),
            ),
        ],
    )
    def test_get_job_status(self, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)

            created_job = Job(
                id="abc_123",
                status={"code": "Initialized"},
                task={"type": JOB_TYPE_LR},
                requester=r,
                project_id="p_123",
            )

            get_status = created_job.get_status()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(get_status, str)
            assert get_status == "Initialized"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "project": {
                            "job": {
                                "model_metrics": [{"name": "r_squared", "value": [0.1]}]
                            }
                        }
                    }
                },
                notraising(),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(Exception, match="An error occurred: .*"),
            ),
        ],
    )
    def test_get_job_results(self, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)

            my_job = Job(
                id="abc_123",
                status={"code": "Initialized"},
                task={"type": JOB_TYPE_LR},
                requester=r,
                project_id="p_123",
            )

            weights, metrics = my_job.get_results()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(metrics, dict)
            assert metrics["r_squared"] == [0.1]
