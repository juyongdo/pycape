class GQLException(Exception):
    pass


class NotAUserException(Exception):
    pass


class InvalidCoordinatorException(Exception):
    pass


class StorageSchemeException(Exception):
    def __init__(self, scheme: str, message: str = None, payload: str = None):
        self.message = message or f"Only s3 locations supported, got {scheme or 'None'}"
        self.payload = payload

    def __str__(self):
        return str(self.message)


class StorageException(Exception):
    def __init__(self, uri: str, message: str = None, payload: str = None):
        self.message = message or f"Invalid s3 bucket provided: {uri}"
        self.payload = payload

    def __str__(self):
        return str(self.message)


class StorageAccessException(Exception):
    def __init__(self, message: str = None, payload: str = None):
        self.message = message or "Resource not accessible."
        self.payload = payload

    def __str__(self):
        return str(self.message)
