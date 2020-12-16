class DataView:
    """
    Instantiating this class allows you to initialize Dataview objects. Dataview objects can be added to projects.
    """

    def __init__(
        self,
        id: str = "",
        name: str = "",
        uri: str = "",
        location: str = "",
        owner_id: str = "",
    ):
        """
        :param id: id
        :param name: name
        :param uri: uri
        :param location: location
        :param owner_id: owner_id
        """
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self.location: str = location
        self.owner_id: str = owner_id

    def __repr__(self):
        return f"<{self.__class__.__name__} ID: {self.id}>"

    def get_input(self):
        """
        Format dict for gql type DataTypeInput
        """
        return {
            k: v
            for k, v in {
                "name": self.name,
                "uri": self.uri,
                "owner_id": self.owner_id,
            }.items()
            if v
        }
