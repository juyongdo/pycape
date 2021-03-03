class Organization:
    """
    Organization represents an organization in Cape.
    """

    def __init__(
        self, id: str = None, name: str = None, label: str = None,
    ):
        """
        :param id: str
        :param name: str
        :param label: str
        """

        self.id: str = id
        self.name: str = name
        self.label: str = label

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, label={self.label})"
