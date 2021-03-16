class GQLException(Exception):
    pass


class StorageSchemeException(Exception):
    def __init__(self, scheme: str, message: str = None, payload: str = None):
        self.message = message or f"only s3 locations supported, got {scheme}"
        self.payload = payload

    def __str__(self):
        return str(self.message)
