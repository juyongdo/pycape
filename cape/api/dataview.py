import pandas as pd
from urllib.error import HTTPError
from datetime import datetime
from IPython import embed
from cape.utils import is_date


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
        :param uri: uri
        :param __location: location
        :param owner_id: owner_id
        """
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self.__location: str = location
        self._owner_id: str = owner_id
        self._user_id: str = user_id
        self.schema: pd.Series = schema

    def __repr__(self):
        return f"<{self.__class__.__name__} ID: {self.id}>"

    @property
    def location(self) -> str:
        """
        Protect location property by validating authorized user is the owner of the DataView
        """
        # TODO: make _user_id and _owner_id only settable upon initilization
        if self._user_id and self._owner_id and self._user_id == self._owner_id:
            return self.uri or self.__locaion

    @property
    def schema(self) -> dict:
        """
        Return schema as pd.Series
        """
        if self._schema:
            return pd.Series(self._schema)
        else:
            return None

    @schema.setter
    def schema(self, s):
        """
        Validate that updates to the schema property are of the correct panda type.
        Converts schema to dictionary to set.
        """
        if isinstance(s, pd.Series):
            self._schema = s.to_dict()
        elif not isinstance(s, type(None)):
            raise Exception(f"Schema is not of type Series")
        else:
            self._schema = None

    def get_input(self):
        """
        Format dict for gql type DataTypeInput
        """
        return {
            k: v
            for k, v in {
                "name": self.name,
                "uri": self.uri,
                "owner_id": self._owner_id,
                # TODO: Pass schema to coordinator
                # "schema": self._schema,
            }.items()
            if v
        }

    def get_schema_from_uri(self):
        def _get_date_cols(dataframe: pd.DataFrame) -> list:
            columns = df.columns
            row_1 = df.iloc[0].values
            date_cols = []

            for i, d in enumerate(row_1):
                if isinstance(d, str) and is_date(d):
                    date_cols.append(columns[i])

            return date_cols

        try:
            df = pd.read_csv(self.uri, nrows=1)
        except (HTTPError, FileNotFoundError):
            raise Exception("Cannot access data resource")

        date_cols = _get_date_cols(df)
        for date_col in date_cols:
            df[date_col] = pd.to_datetime(df[date_col])

        self.schema = df.dtypes

