import pytest
import responses
from cape.cape import Cape
from cape.exceptions import GQLException

host = "http://cape.com"
token = "01EQXZ0FKYNF8MX4MJZPWQ4KTA,Ae-gaS4Ey_Hz9eq_MvGJigiwx4coy8vDmA"


@responses.activate
def test_login():
    pass


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
