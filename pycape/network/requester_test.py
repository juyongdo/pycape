from contextlib import contextmanager

import pytest
import responses

from tests.fake import FAKE_HOST

from ..exceptions import GQLException
from .requester import Requester


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
        responses.add(responses.POST, f"{FAKE_HOST}/v1/query", body=body, status=status)
        r = Requester(endpoint=FAKE_HOST)
        r._gql_req(query=query, variables=variables)
