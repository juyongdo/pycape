from .api_token import create_api_token
from .base64 import Base64


def test_api_token():
    token_id = "imatokenid"
    secret = "aaaabbbbccccdddd"
    token = create_api_token(token_id, secret)

    assert token.token_id == token_id
    assert token.secret == str(Base64(secret))
    assert token.version == 1
