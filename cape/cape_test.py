import contextlib

import pytest
import responses
from io import StringIO

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
            out = StringIO()
            c.list_projects(out=out)

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
