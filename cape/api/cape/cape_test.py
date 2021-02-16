import contextlib
import os
from io import StringIO

import pytest
import responses

from .cape import Cape
from ..project.project import Project
from ...exceptions import GQLException
from ...network import NotAUserException
from tests.fake import FAKE_HOST, FAKE_TOKEN


@contextlib.contextmanager
def notraising():
    yield


class TestCape:
    @responses.activate
    @pytest.mark.parametrize(
        "token,json,query_json,status,exception",
        [
            (
                FAKE_TOKEN,
                {"token": "cookie", "user_id": "user_1"},
                {"data": {"me": {"__typename": "MeResponse"}}},
                200,
                notraising(),
            ),
            (
                FAKE_TOKEN,
                {"token": "cookie", "user_id": "user_1"},
                {"data": {"me": {"__typename": "UnverifiedError"}}},
                200,
                pytest.raises(NotAUserException),
            ),
            (None, {}, {}, 200, pytest.raises(Exception, match="No token provided")),
            (
                "abc123",
                {},
                {},
                200,
                pytest.raises(Exception, match="Bad token provided"),
            ),
            (
                FAKE_TOKEN,
                {},
                {},
                400,
                pytest.raises(
                    Exception, match="400 Client Error: Bad Request for url:*"
                ),
            ),
        ],
    )
    def test_login(self, token, json, query_json, status, exception):
        os.environ["CAPE_TOKEN"] = ""
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/login", json=json, status=status
            )

            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=query_json, status=status
            )
            out = StringIO()
            c = Cape(endpoint=FAKE_HOST, out=out)
            c.login(token=token)

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert output == "Login successful"

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
            out = StringIO()
            c = Cape(endpoint=FAKE_HOST, out=out)
            c.list_projects()

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert output == (
                "PROJECT ID    NAME        LABEL"
                "\n------------  ----------  ----------\n"
                "abc123        my-project  my-project"
            )

    @responses.activate
    @pytest.mark.parametrize(
        "id,label,json,exception",
        [
            (
                "project_123",
                None,
                {"data": {"project": {"id": "project_123", "label": "my-project"}}},
                notraising(),
            ),
            (
                None,
                "my-project",
                {"data": {"project": {"id": "project_123", "label": "my-project"}}},
                notraising(),
            ),
            (
                "project_123",
                None,
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_get_project(self, id, label, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            c = Cape(endpoint=FAKE_HOST)
            project = c.get_project(id=id, label=label)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(project, Project)
            assert project.id == json.get("data", {}).get("project", {}).get("id")
            assert project.label == json.get("data", {}).get("project", {}).get("label")

    @responses.activate
    @pytest.mark.parametrize(
        "args,json,exception",
        [
            (
                {
                    "name": "my-project",
                    "owner": "owner_123",
                    "description": "Test org desc.",
                },
                {
                    "data": {
                        "createProject": {
                            "id": "new_project_123",
                            "name": "my-project",
                            "owner": "owner_123",
                        }
                    }
                },
                notraising(),
            ),
            (
                {"name": "my-project", "owner": "owner_123"},
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_create_project(self, args, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            c = Cape(endpoint=FAKE_HOST)
            project = c.create_project(**args)

        if isinstance(exception, contextlib._GeneratorContextManager):
            assert isinstance(project, Project)

            assert project.id == json.get("data", {}).get("createProject", {}).get("id")
            assert project.name == args.get("name")

    @responses.activate
    @pytest.mark.parametrize(
        "id,json,exception",
        [
            (
                "project_123",
                {"data": {"archiveProject": {"archivedProjectId": "project_123"}}},
                notraising(),
            ),
            (
                "project_123",
                {"errors": [{"message": "something went wrong"}]},
                pytest.raises(GQLException, match="An error occurred: .*"),
            ),
        ],
    )
    def test_remove_project(self, id, json, exception, mocker):
        with exception:
            responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json=json,
            )
            out = StringIO()
            c = Cape(endpoint=FAKE_HOST, out=out)
            c.remove_project(id=id)

        if isinstance(exception, contextlib._GeneratorContextManager):
            output = out.getvalue().strip()
            assert isinstance(output, str)
            assert output == "Project (project_123) deleted"
