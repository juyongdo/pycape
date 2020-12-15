import pytest
import responses
from cape.cape import Cape
from cape.exceptions import GQLException

host = "http://cape.com"
token = "abc,123"


@responses.activate
@pytest.mark.parametrize(
    "token,json,status,exception,response",
    [
        (token, {"token": "cookie"}, 200, None, "success"),
        (None, {}, 200, "No token provided", None),
        ("abc123", {}, 200, "Bad token provided", None),
        (token, {}, 400, "400 Client Error: Bad Request for url:*", None),
    ],
)
def test_login_error(token, json, status, exception, response):
    with pytest.raises(Exception, match=exception):
        resp = responses.add(
            responses.POST, f"{host}/v1/login", json=json, status=status
        )
        c = Cape(endpoint=host, token=token)
        r = c.login()

        assert r == response


@responses.activate
def test_list_projects():
    responses.add(
        responses.POST,
        f"{host}/v1/query",
        json={
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
    )
    c = Cape(token=token, endpoint=host)
    projects = c.list_projects()

    assert len(projects) == 1
    assert projects[0]["id"] == "abc123"


@responses.activate
def test_list_projects_error():
    with pytest.raises(GQLException, match="An error occurred: .*"):
        responses.add(
            responses.POST,
            f"{host}/v1/query",
            json={"errors": [{"message": "something went wrong"}]},
        )

        c = Cape(token=token, endpoint=host)
        c.list_projects()
