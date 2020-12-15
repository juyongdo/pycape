from cape.network.requester import authenticate


class Cape:
    """
    This is the main class you instantiate to access the Cape DS API. Token parameter is required for authentication.
    """

    def __init__(self, token):
        """
        :param token: token (required)
        """
        self.__requester = authenticate(token=token)

    def login(self):
        '''
        Calls /v1/login and passes token_id and secret parsed from token passed to Requester.
        '''
        self.__requester.login()
