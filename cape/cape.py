from cape.network.requester import Requester
from cape.api.project import Project


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

    def login(self, token: str):
        """
        :calls: `POST /v1/login`
        :param token: token
        """
        self.__user_id = self.__requester.login(token=token)

    def list_projects(self):
        """
        :calls: `query projects`
        :rtype: [:class:`cape.api.project.project`]
        """
        projects = self.__requester.list_projects()
        return [
            Project(requester=self.__requester, user_id=self.__user_id, **p)
            for p in projects
        ]

    def get_project(self, id: str) -> Project:
        """
        :calls: `query project`
        :rtype: :class:`cape.api.project.project`
        """
        project = self.__requester.get_project(id=id)
        return Project(requester=self.__requester, user_id=self.__user_id, **project)
