import sys

from tabulate import tabulate

from cape.api.project import Project
from cape.network.requester import Requester


class Cape:
    """
    This is the main class you instantiate to access the Cape DS API. Token parameter is required for authentication.
    """

    def __init__(self, out=sys.stdout, endpoint: str = None):
        """
        :param endpoint: endpoint
        """
        self.__requester = Requester(endpoint=endpoint)
        self.__user_id = None
        self._out = out

    def login(self, token: str = None) -> str:
        """
        :calls: `POST /v1/login`
        :param token: token
        """
        self.__user_id = self.__requester.login(token=token)
        return self._out.write("Login successful\n")

    def list_projects(self) -> str:
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
        return self._out.write(tabulate(format_projects, headers="keys") + "\n")

    def get_project(self, id: str = None, label: str = None) -> Project:
        """
        :calls: `query project`
        :rtype: :class:`cape.api.project.project`
        """
        project = self.__requester.get_project(id=id, label=label)
        return Project(requester=self.__requester, user_id=self.__user_id, **project)

    def create_project(self, name: str, owner: str, description: str = None) -> Project:
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
