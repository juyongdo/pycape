import contextlib

import pytest

from cape.network.base64 import Base64
from cape.network.base64 import from_string


@contextlib.contextmanager
def notraising():
    yield


def test_base64():
    b64 = Base64("heythere")
    assert "aGV5dGhlcmU" == str(b64)


@pytest.mark.parametrize(
    "string,exception",
    [
        ("ABCD", notraising(),),
        ("ABCDE", pytest.raises(Exception, match="Bad token provided: *"),),
    ],
)
def test_from_string(string, exception):
    with exception:
        b64 = from_string(string)

    if isinstance(exception, contextlib._GeneratorContextManager):
        assert string == str(b64)
