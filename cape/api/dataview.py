class DataView:
    """
    Dataview objects keep track of the business logic around datasets. Dataviews can be added to projects.
    """

    def __init__(
        self,
        id: str = None,
        name: str = None,
        uri: str = None,
        location: str = None,
        owner_id: str = None,
        user_id: str = None,
        schema: dict = None,
    ):
        """
        :param id: id
        :param name: name
        :param __uri: uri
        :param __location: location
        :param owner_id: owner_id
        """
        self.id: str = id
        self.name: str = name
        self.__uri: str = uri
        self.__location: str = location
        self.owner_id: str = owner_id
        self.user_id: str = user_id
        self.schema: dict = schema

    def __repr__(self):
        return f"<{self.__class__.__name__} ID: {self.id}>"

    @property
    def location(self) -> str:
        # return property if the owner_id matches authenticated user_id
        if self.user_id and self.owner_id and self.user_id == self.owner_id:
            return self.__uri

    def _get_input(self):
        """
        Format dict for gql type DataTypeInput
        """
        return {
            k: v
            for k, v in {
                "name": self.name,
                "uri": self.__uri,
                "owner_id": self.owner_id,
            }.items()
            if v
        }
