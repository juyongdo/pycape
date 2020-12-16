import pytest
import responses
from contextlib import contextmanager

from cape.exceptions import GQLException
from cape.network.requester import Requester


host = "http://cape.com"
token = "abc,123"


@contextmanager
def notraising():
    yield


@responses.activate
@pytest.mark.parametrize(
    "query,variables,body,status,exception",
    [
        ("", {}, '{"data": {}}', 200, notraising()),
        (
            "",
            {},
            '{"invalid-json": {"abc": "abc",}}',
            422,
            pytest.raises(Exception, match="422 Client Error:*"),
        ),
        (
            "",
            {},
            '{"errors": []}',
            200,
            pytest.raises(GQLException, match="An error occurred: .*"),
        ),
    ],
)
def test_gql_req(query, variables, body, status, exception):
    with exception:
        responses.add(responses.POST, f"{host}/v1/query", body=body, status=status)
        r = Requester(endpoint=host, token=token)
        r._gql_req(query=query, variables=variables)
