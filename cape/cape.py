import sys

from tabulate import tabulate

from cape.api.project import Project
from cape.network.requester import Requester


class Cape:
    """
    This is the main class you instantiate to access the Cape DS API. Token parameter is required for authentication.
    """

    def __init__(self, endpoint: str = None):
        """
        :param endpoint: endpoint
        """
        self.__requester = Requester(endpoint=endpoint)
        self.__user_id = None

    def login(self, token: str = None, out=sys.stdout):
        """
        :calls: `POST /v1/login`
        :param token: token
        """
        self.__user_id = self.__requester.login(token=token)
        return out.write("Login successful\n")

    def list_projects(self, out=sys.stdout):
        """
        :calls: `query projects`
        :rtype: string
        """
        projects = self.__requester.list_projects()
        get_project_values = [Project(user_id=self.__user_id, **p) for p in projects]
        format_projects = {
            "PROJECT ID": [x.id for x in get_project_values],
            "NAME": [x.name for x in get_project_values],
            "LABEL": [x.label for x in get_project_values],
        }
        return out.write(tabulate(format_projects, headers="keys") + "\n")

    def get_project(self, id: str = None, label: str = None) -> Project:
        """
        :calls: `query project`
        :rtype: :class:`cape.api.project.project`
        """
        project = self.__requester.get_project(id=id, label=label)
        return Project(requester=self.__requester, user_id=self.__user_id, **project)

    def create_project(self, name: str, owner: str, description: str = None):
        """
        :calls: `mutation createProject`
        :param name: string
        :param owner: string
        :param description: string
        :rtype: [:class:`cape.api.project.Project`]
        """
        project = self.__requester.create_project(
            name=name, owner=owner, description=description
        )
        return Project(requester=self.__requester, user_id=self.__user_id, **project)
