import pytest
import responses
import contextlib

from cape.network.requester import Requester
from cape.api.job.job import Job
from cape.api.job.multiplication_job import MultiplicationJob
from cape.api.project.project import Project
from cape.exceptions import GQLException
from tests.fake import fake_dataframe, FAKE_HOST


@contextlib.contextmanager
def notraising():
    yield


class TestJob:
    def test__repr__(self):
        id = "abc123"
        job_type = "MULTIPLICATION"

        j = Job(id=id, job_type=job_type)

        assert repr(j) == f"<{j.__class__.__name__} (id={id}, job_type={job_type})>"

    @responses.activate
    @pytest.mark.parametrize(
        "args,json,exception",
        [
            (
                {"job_type": "MULTIPLICATION"},
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
                {"job_type": "MULTIPLICATION"},
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
            ({"data": {"assignTaskRoles": {"id": "abc123"}}}, notraising()),
            (
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_assign_job_roles(self, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            r = Requester(endpoint=FAKE_HOST)
            my_job = Job(requester=r, id="job_123", job_type="MULTIPLICATION")

            job_with_roles = my_job.assign_job_roles(
                job_roles_input={"task_role_1": "alice"}
            )

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(job_with_roles, dict)
            assert job_with_roles.get("id") == "abc123"

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
            my_job = Job(requester=r, id="job_123", job_type="MULTIPLICATION")

            submitted_job = my_job.submit_job()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(submitted_job, dict)
            assert submitted_job.get("id") == "abc123"
