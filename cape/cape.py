from cape.network.requester import authenticate


class Cape:
    """
    This is the main class you instantiate to access the Cape DS API. Token parameter is required for authentication.
    """

    def __init__(self, token: str = None, endpoint: str = None):
        """
        :param token: token
        :param endpoint: endpoint
        """
        self.__requester = authenticate(token=token, endpoint=endpoint)
        self.__user_id = None

    def login(self):
        """
        :calls: `POST /v1/login`
        Passes token_id and secret parsed from api token to Requester.
        """
        self.__user_id = self.__requester.login()

    def list_projects(self):
        """
        :calls: `query projects`
        :rtype: list
        """
        d = self.__requester.list_projects()
        return d

    def add_dataview(self, project_id: str = None, name: str = None, uri: str = None):
        """
        :calls: `mutation addDataView`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        d = self.__requester.add_dataview(
            project_id=project_id, name=name, uri=uri, user_id=self.__user_id
        )
        return d

    def list_dataviews(self):
        """
        Queries gql for list of dataviews by project
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: list
        """
        d = self.__requester.list_dataviews()
        return d

    def get_dataview(self, project_id, **kwargs):
        """
        Queries gql for a dataview in a project
        :calls: `query project`
        :param project_id: string
        :param id: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        d = self.__requester.get_dataview(project_id=project_id, **kwargs)
        return d
