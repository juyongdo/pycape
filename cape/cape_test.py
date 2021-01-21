import contextlib

import pytest
import responses

from cape.api.project.project import Project
from cape.cape import Cape
from cape.exceptions import GQLException
from tests.fake import FAKE_HOST
from tests.fake import FAKE_TOKEN


@contextlib.contextmanager
def notraising():
    yield


class TestCape:
    @responses.activate
    @pytest.mark.parametrize(
        "token,json,status,exception",
        [
            (FAKE_TOKEN, {"token": "cookie", "user_id": "user_1"}, 200, notraising()),
            (None, {}, 200, pytest.raises(Exception, match="No token provided")),
            ("abc123", {}, 200, pytest.raises(Exception, match="Bad token provided")),
            (
                FAKE_TOKEN,
                {},
                400,
                pytest.raises(
                    Exception, match="400 Client Error: Bad Request for url:*"
                ),
            ),
        ],
    )
    def test_login(self, token, json, status, exception):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/login", json=json, status=status
            )
            c = Cape(endpoint=FAKE_HOST)
            c.login(token=token)

    @responses.activate
    @pytest.mark.parametrize(
        "json,exception",
        [
            (
                {
                    "data": {
                        "projects": [
                            {
                                "id": "abc123",
                                "label": "my-project",
                                "name": "my-project",
                                "description": "we are here to do some data science",
                            }
                        ]
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
    def test_list_projects(self, json, exception):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            c = Cape(endpoint=FAKE_HOST)
            projects = c.list_projects()

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert len(projects) == 1
            assert isinstance(projects[0], Project)
            assert projects[0].id == "abc123"

    @responses.activate
    @pytest.mark.parametrize(
        "id,json,exception",
        [
            (
                "project_123",
                {"data": {"project": {"id": "project_123", "label": "my-project"}}},
                notraising(),
            ),
            (
                "project_123",
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_get_project(self, id, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            c = Cape(endpoint=FAKE_HOST)
            project = c.get_project(id=id)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(project, Project)
            assert project.id == id
