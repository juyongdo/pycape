import contextlib
import os
from io import StringIO

import pytest
import responses

from .linear_regression_project import list_projects

from tests.fake import FAKE_HOST, FAKE_TOKEN
from IPython import embed


class TestExampleLinReg:
    @responses.activate
    def test_list_projects(self):
        responses.add(
                responses.POST, f"{FAKE_HOST}/v1/query", json={"data": {"me": {"__typename": "MeResponse"}}}
            )
        list_projects()
        
        embed()