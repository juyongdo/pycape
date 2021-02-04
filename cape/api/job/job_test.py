import contextlib

import pytest
import responses

from cape.api.dataview.dataview import DataView
from cape.api.job import VerticalLinearRegressionJob
from cape.api.job.job import Job
from cape.api.project.project import Project
from cape.vars import JOB_TYPE_LR, JOB_STATUS_CREATED
from cape.network.requester import Requester
from tests.fake import FAKE_HOST


@contextlib.contextmanager
def notraising():
    yield


class TestJob:
    def test__repr__(self):
        id = "abc123"

        j = Job(id=id, job_type=JOB_TYPE_LR, status={"code": JOB_STATUS_CREATED})

        assert (
            repr(j)
            == f"{j.__class__.__name__}(id={id}, job_type={JOB_TYPE_LR}, status={JOB_STATUS_CREATED})"
        )

    @responses.activate
    @pytest.mark.parametrize(
        "json,dataview_x,dataview_y,dataview_col_x,dataview_col_y,exception",
        [
            (
                {"data": {"initializeSession": {"id": "session_123"}}},
                DataView(id="dv_1", name="my-data", uri="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", uri="s3://my-data-2.csv"),
                "123",
                "123",
                notraising(),
            ),
            (
                {"data": {"initializeSession": {"id": "session_123"}}},
                DataView(name="my-data", uri="s3://my-data.csv"),
                DataView(name="my-data_1", uri="s3://my-data-2.csv"),
                "123",
                "123",
                pytest.raises(
                    Exception,
                    match="DataView Missing Properties: X DataView ID, Y DataView ID",
                ),
            ),
            (
                {"data": {"initializeSession": {"id": "session_123"}}},
                DataView(id="dv_1", name="my-data", uri="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", uri="s3://my-data-2.csv"),
                None,
                None,
                pytest.raises(
                    Exception,
                    match="DataView Missing Properties: X DataView columns, Y DataView columns",
                ),
            ),
            (
                {"errors": [{"message": "something went wrong"}]},
                DataView(id="dv_1", name="my-data", uri="s3://my-data.csv"),
                DataView(id="dv_2", name="my-data_1", uri="s3://my-data-2.csv"),
                "123",
                "123",
                pytest.raises(Exception, match="An error occurred: .*"),
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
            my_job = VerticalLinearRegressionJob(**task_config)

            submitted_job = my_project.submit_job(my_job)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(submitted_job, VerticalLinearRegressionJob)
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

            my_job = VerticalLinearRegressionJob(
                id="abc_123", project_id="123", requester=r
            )

            get_status = my_job.get_status()

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

            my_job = VerticalLinearRegressionJob(
                id="abc_123", project_id="123", requester=r
            )

            weights, metrics = my_job.get_results()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(metrics, list)
            assert metrics[0].get("name") == "r_squared"
