
import os
import requests

from cape.network.api_token import APIToken
from cape.network import base64


def authenticate(token: str):
    if not token:
        raise Exception(f"No token provided")

    endpoint = os.environ.get(
        "CAPE_COORDINATOR", "http://localhost:8080")

    return Requester(endpoint, token)


class Requester:
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.gql_endpoint = self.endpoint + "/v1/query"
        self.api_token = APIToken(token)
        self.session = requests.Session()
        self.token = ""

    def login(self):
        resp = self.session.post(
            self.endpoint + "/v1/login",
            json={"token_id": self.api_token.token_id,
                  "secret": self.api_token.secret},
        )

        json = resp.json()
        self.token = base64.from_string(json["token"])
