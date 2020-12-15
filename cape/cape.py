import requests

from cape.exceptions import GQLException


class Cape:
    def __init__(self, token: str, endpoint: str = "https://demo.capeprivacy.com"):
        self.token = token
        self.endpoint = endpoint
        self.gql_endpoint = f"{self.endpoint}/v1/query"

        self.session = requests.session()

    def login(self):
        # TODO(grace)
        pass

    def list_projects(self):
        query = """
        query ListProjects {
            projects {
                id,
                name,
                label,
                description
            }
        }
        """
        r = self.session.post(self.gql_endpoint, {"query": query})
        r.raise_for_status()
        j = r.json()
        if "errors" in j:
            raise GQLException(f"an error occurred: {j['errors']}")

        return j["data"]["projects"]
