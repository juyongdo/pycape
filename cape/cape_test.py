import pytest
import responses
from contextlib import contextmanager

from cape.cape import Cape
from cape.exceptions import GQLException


host = "http://cape.com"
token = "abc,123"


@contextmanager
def notraising():
    yield


@responses.activate
@pytest.mark.parametrize(
    "token,json,status,exception",
    [
        (token, {"token": "cookie"}, 200, notraising()),
        (None, {}, 200, pytest.raises(Exception, match="No token provided")),
        ("abc123", {}, 200, pytest.raises(Exception, match="Bad token provided")),
        (
            token,
            {},
            400,
            pytest.raises(Exception, match="400 Client Error: Bad Request for url:*"),
        ),
    ],
)
def test_login(token, json, status, exception):
    with exception:
        responses.add(responses.POST, f"{host}/v1/login", json=json, status=status)
        c = Cape(endpoint=host, token=token)
        c.login()


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
def test_list_projects(json, exception):
    with exception:
        responses.add(
            responses.POST, f"{host}/v1/query", json=json,
        )
        c = Cape(token=token, endpoint=host)
        projects = c.list_projects()

    if exception == notraising():
        assert len(projects) == 1
        assert projects[0]["id"] == "abc123"
