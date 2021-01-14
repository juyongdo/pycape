import os
import requests
from typing import Optional

from cape.network.api_token import APIToken
from cape.network import base64
from cape.exceptions import GQLException


class Requester:
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint or os.environ.get(
            "CAPE_COORDINATOR", "http://localhost:8080"
        )
        self.gql_endpoint = self.endpoint + "/v1/query"
        self.session = requests.Session()

    def login(self, token: str):
        if not token:
            raise Exception("No token provided")

        self.token = token
        self.api_token = APIToken(self.token)

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

    def get_project(self, id: str):
        return self._gql_req(
            query="""
            query GetProject($id: String!) {
                project(id: $id) {
                    id,
                    name,
                    label,
                    description
                }
            }
            """,
            variables={"id": id},
        ).get("project")

    def add_dataview(self, project_id: str, data_view_input: dict):
        return self._gql_req(
            query="""
            mutation AddDataView (
              $project_id: String!,
              $data_view_input: DataViewInput!
            ) {
              addDataView(project_id: $project_id, data_view_input: $data_view_input) {
                id
                name
                location
                owner {
                  ... on User {
                    id
                  }
                  ... on Organization {
                    id
                  }
                },
                schema { name, schema_type }
              }
            }
            """,
            variables={"project_id": project_id, "data_view_input": data_view_input},
        ).get("addDataView")

    def list_dataviews(self, project_id: str):
        return (
            self._gql_req(
                query="""
            query ListDataViews($id: String!) {
                project(id: $id) {
                    data_views {
                      id,
                      name,
                      location,
                      owner {
                        ... on User {
                          id
                        }
                        ... on Organization {
                          id
                        }
                      },
                      schema { name, schema_type }
                    }
                }
            }
            """,
                variables={"id": project_id},
            )
            .get("project", {})
            .get("data_views")
        )

    def get_dataview(self, project_id, **kwargs):
        if not kwargs.get("id") and not kwargs.get("uri"):
            raise Exception("Required identifier id or uri not specified.")
        return (
            self._gql_req(
                query="""
            query GetDataView($id: String, $project_id: String, $uri: String) {
                project(id: $project_id) {
                    data_views(id: $id, uri: $uri) {
                      id,
                      name,
                      location,
                      owner {
                        ... on User {
                          id
                        }
                        ... on Organization {
                          id
                        }
                      },
                      schema { name, schema_type }
                    }
                }
            }
            """,
                variables={
                    "project_id": project_id,
                    "id": kwargs.get("id"),
                    "uri": kwargs.get("uri"),
                },
            )
            .get("project", {})
            .get("data_views")
        )

    def create_job(self, project_id, task_type, task_config):
        return self._gql_req(
            query="""
            mutation CreateTask($project_id: String!, $task_type: TaskType!, $task_config: TaskConfigInput) {
                createTask(project_id: $project_id, task_type: $task_type, task_config: $task_config) {
                  id
                  computation
                }
            }
            """,
            variables={
                "project_id": project_id,
                "task_type": task_type,
                "task_config": task_config,
            },
        ).get("createTask", {})

    def assign_job_roles(self, job_id, job_roles_input):
        return self._gql_req(
            query="""
            mutation AssignTaskRoles($task_id: String!, $task_roles: TaskRolesInput!) {
                assignTaskRoles(task_id: $task_id, task_roles: $task_roles) {
                  id
                }
            }
            """,
            variables={"task_id": job_id, "task_roles": job_roles_input},
        ).get("assignTaskRoles", {})

    def submit_job(self, job_id):
        return self._gql_req(
            query="""
            mutation InitializeSession($task_id: String!) {
                initializeSession(task_id: $task_id) {
                  id
                  status {
                    runtime
                  }
                }
            }
            """,
            variables={"task_id": job_id},
        ).get("initializeSession", {})
