import pytest
import responses
import contextlib

from cape.cape import Cape
from cape.api.dataview import DataView
from cape.exceptions import GQLException
from tests.fake import fake_dataframe, FAKE_HOST, FAKE_TOKEN


@contextlib.contextmanager
def notraising():
    yield


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
            pytest.raises(Exception, match="400 Client Error: Bad Request for url:*"),
        ),
    ],
)
def test_login(token, json, status, exception):
    with exception:
        responses.add(responses.POST, f"{FAKE_HOST}/v1/login", json=json, status=status)
        c = Cape(endpoint=FAKE_HOST, token=token)
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
            responses.POST, f"{FAKE_HOST}/v1/query", json=json,
        )
        c = Cape(token=FAKE_TOKEN, endpoint=FAKE_HOST)
        projects = c.list_projects()

    if isinstance(exception, contextlib._GeneratorContextManager):
        assert len(projects) == 1
        assert projects[0]["id"] == "abc123"


@responses.activate
@pytest.mark.parametrize(
    "json,exception",
    [
        (
            {
                "data": {
                    "addDataView": {
                        "id": "abc123",
                        "name": "my-data",
                        "location": "s3://my-data.csv",
                    }
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
def test_add_dataview(json, exception, mocker):
    with exception:
        mocker.patch("cape.api.dataview.pd.read_csv", return_value=fake_dataframe())
        responses.add(
            responses.POST, f"{FAKE_HOST}/v1/query", json=json,
        )
        c = Cape(token=FAKE_TOKEN, endpoint=FAKE_HOST)
        dataview = c.add_dataview(
            project_id="123", name="my-data", uri="s3://my-data.csv"
        )

    if isinstance(exception, contextlib._GeneratorContextManager):
        assert isinstance(dataview, DataView)
        assert dataview.id == "abc123"


@responses.activate
@pytest.mark.parametrize(
    "json,exception",
    [
        (
            {
                "data": {
                    "project": {
                        "id": "abc123",
                        "label": "my-project",
                        "data_views": [
                            {
                                "id": "def123",
                                "name": "my-dataview",
                                "location": "https",
                                "schema": [{"name": "col_1", "schema_type": "string"}],
                            }
                        ],
                    }
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
def test_list_dataviews(json, exception, mocker):
    with exception:
        mocker.patch("cape.api.dataview.pd.read_csv", return_value=fake_dataframe())
        responses.add(
            responses.POST, f"{FAKE_HOST}/v1/query", json=json,
        )
        c = Cape(token=FAKE_TOKEN, endpoint=FAKE_HOST)
        dataviews = c.list_dataviews()

    if isinstance(exception, contextlib._GeneratorContextManager):
        assert isinstance(dataviews, list)
        assert dataviews[0]["id"] == "def123"
        assert isinstance(dataviews[0]["schema"], list)
        assert dataviews[0]["schema"][0]["name"] == "col_1"
