
import os
import requests
from typing import Optional

from cape.network.api_token import APIToken
from cape.network import base64
from cape.exceptions import GQLException


def authenticate(token: str, endpoint: str = None):
    if not token:
        raise Exception(f"No token provided")

    endpoint = endpoint or os.environ.get(
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

    def gql_req(self, query: str, variables: Optional[dict]):
        input_json = {"query": query, "variables": {}}
        if variables is not None:
            input_json["variables"] = variables

        r = self.session.post(self.gql_endpoint, json=input_json)
        r.raise_for_status()
        j = r.json()
        if "errors" in j:
            raise GQLException(f"An error occurred: {j['errors']}")
        return j["data"]

    def list_projects(self):
        return self.gql_req(query="""
            query ListProjects {
                projects {
                    id,
                    name,
                    label,
                    description
                }
            }
            """, variables=None).get('projects')
