import pytest
import responses
import contextlib

from cape.network.requester import Requester
from cape.api.job.job import Job
from cape.api.job import VerticalLinearRegressionJob
from cape.api.project.project import Project
from cape.api.dataview.dataview import DataView
from cape.exceptions import GQLException
from cape.vars import JOB_TYPE_LR
from tests.fake import FAKE_HOST


@contextlib.contextmanager
def notraising():
    yield


class TestJob:
    def test__repr__(self):
        id = "abc123"

        j = Job(id=id, job_type=JOB_TYPE_LR)

        assert repr(j) == f"<{j.__class__.__name__} (id={id}, job_type={JOB_TYPE_LR})>"

    @responses.activate
    @pytest.mark.parametrize(
        "args,json,exception",
        [
            (
                {"job_type": JOB_TYPE_LR},
                {"data": {"createTask": {"id": "abc123"}}},
                notraising(),
            ),
            (
                {"job_type": "A TASK"},
                {"data": {"createTask": {"id": "abc123"}}},
                pytest.raises(Exception, match="Job initialized with invalid job type"),
            ),
            (
                {"job_type": None},
                {"data": {"createTask": {"id": "abc123"}}},
                pytest.raises(
                    Exception, match="Jobs cannot be initialized without a job type"
                ),
            ),
            (
                {"job_type": JOB_TYPE_LR},
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_create_job(self, args, json, exception, mocker):
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
            my_job = Job(requester=r, **args)

            created_job = my_project.create_job(job=my_job)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(created_job, Job)
            assert created_job.id == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            ({"data": {"initializeSession": {"id": "abc123"}}}, notraising()),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(Exception, match="An error occurred: .*"),
            ),
        ],
    )
    def test_submit_job(self, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_job = Job(requester=r, id="job_123", job_type=JOB_TYPE_LR)

            submitted_job = my_job.submit_job()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(submitted_job, dict)
            assert submitted_job.get("id") == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception", [({"data": {"createTask": {"id": "abc123"}}}, notraising())],
    )
    def test_create_lr_job(self, json, exception, mocker):
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

            my_data_view_1 = DataView(id="dv_1", name="my-data", uri="s3://my-data.csv")
            my_data_view_2 = DataView(
                id="dv_2", name="my-data_1", uri="s3://my-data-2.csv"
            )

            task_config = {
                "x_train_dataview": my_data_view_1,
                "x_train_data_cols": ["123"],
                "y_train_dataview": my_data_view_2,
                "y_train_data_cols": ["123"],
            }
            my_job = VerticalLinearRegressionJob(requester=r, **task_config)

            created_job = my_project.create_job(job=my_job)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(created_job, VerticalLinearRegressionJob)
            assert created_job.id == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "initializeSession": {
                            "id": "session_123",
                            "task": {"id": "abc123"},
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
    def test_submit_lr_job(self, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_job = VerticalLinearRegressionJob(requester=r, id="job_123")

            submitted_job = my_job.submit_job()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(submitted_job, VerticalLinearRegressionJob)
            assert submitted_job.id == "abc123"
