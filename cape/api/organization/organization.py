class Organization:
    def __init__(
        self, id: str = None, name: str = None,
    ):
        """
        :param id: str
        :param name: str
        """

        self.id: str = id
        self.name: str = name

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name})>"
