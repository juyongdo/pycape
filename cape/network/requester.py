import os
import requests
from typing import Optional

from cape.network.api_token import APIToken
from cape.network import base64
from cape.exceptions import GQLException
from cape.api.dataview import DataView


def authenticate(token: str, endpoint: str = None):
    if not token:
        raise Exception("No token provided")

    endpoint = endpoint or os.environ.get("CAPE_COORDINATOR", "http://localhost:8080")

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
            json={"token_id": self.api_token.token_id, "secret": self.api_token.secret},
        )
        resp.raise_for_status()
        json = resp.json()

        self.token = base64.from_string(json["token"])
        return json["user_id"]

    def _gql_req(self, query: str, variables: Optional[dict]):
        input_json = {"query": query, "variables": {}}
        if variables is not None:
            input_json["variables"] = variables

        r = self.session.post(self.gql_endpoint, json=input_json)

        try:
            j = r.json()
        except ValueError:
            r.raise_for_status()

        if "errors" in j:
            raise GQLException(f"An error occurred: {j['errors']}")
        return j["data"]

    def list_projects(self):
        return self._gql_req(
            query="""
            query ListProjects {
                projects {
                    id,
                    name,
                    label,
                    description
                }
            }
            """,
            variables=None,
        ).get("projects")

    def add_dataview(self, project_id, name, uri, user_id, **kwargs):
        dv = DataView(name=name, uri=uri, user_id=user_id, **kwargs)
        dv.get_schema_from_uri()
        dv_input = dv.get_input()
        return DataView(
            **self._gql_req(
                query="""
            mutation addDataView (
              $project_id: String!,
              $data_view_input: DataViewInput!
            ) {
              addDataView(project_id: $project_id, data_view_input: $data_view_input) {
                id
                name
                location
                schema
              }
            }
            """,
                variables={"project_id": project_id, "data_view_input": dv_input},
            ).get("addDataView")
        )

    def list_dataviews(self):
        return (
            self._gql_req(
                query="""
            query ListDataViews(id: ID!) {
                project(id: $id) {
                    id,
                    label,
                    data_views {
                      id,
                      name,
                      location,
                      schema { name, schemaType }
                    }
                }
            }
            """,
                variables=None,
            )
            .get("project", {})
            .get("data_views")
        )
