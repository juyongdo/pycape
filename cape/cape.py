from cape.network.requester import authenticate


class Cape:
    """
    This is the main class you instantiate to access the Cape DS API. Token parameter is required for authentication.
    """

    def __init__(self, token: str = None, endpoint: str = None):
        """
        :param token: token (required)
        :param endpoint: endpoint
        """
        self.__requester = authenticate(token=token, endpoint=endpoint)
        self.__user_id = None

    def login(self):
        """
        Calls /v1/login and passes token_id and secret parsed from api token passed to Requester.
        """
        self.__user_id = self.__requester.login()

    def list_projects(self):
        """
        Add a dataview to a project
        """
        d = self.__requester.list_projects()
        return d

    def add_dataview(self, project_id, name, uri, **kwargs):
        d = self.__requester.add_dataview(
            project_id=project_id, name=name, uri=uri, user_id=self.__user_id, **kwargs
        )
        return d

    def list_dataviews(self):
        """
        Queries gql api for list of dataviews
        """
        d = self.__requester.list_dataviews()
        return d
