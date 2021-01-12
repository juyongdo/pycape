import json
import pandas as pd

from urllib.error import HTTPError
from marshmallow import Schema, fields

from cape.utils import filter_date


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
        owner: dict = None,
        schema: dict = None,
        user: str = None,
    ):
        """
        :param id: id
        :param name: name
        :param uri: uri
        :param _location: location
        :param _owner: _owner
        :param schema: schema
        """
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self._location: str = location
        self._owner: str = owner
        self._owner_id: str = owner_id
        self._user_id: str = user_id
        self.schema: pd.Series = schema
        self._user: str = user

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"

    @property
    def location(self) -> str:
        """
        Protect location property by validating authorized user is the owner of the DataView
        """
        # TODO: make _user and _owner only settable upon initilization
        if self._user and self._owner and self._user == self._owner["id"]:
            return self.uri or self._location

    @property
    def schema(self) -> dict:
        if hasattr(self, "_schema"):
            return {s.get("name"): s.get("schema_type") for s in self._schema}

    @schema.setter
    def schema(self, s):
        """
        Validate that updates to the schema property are lists.
        """
        # Wrap if block in try/except block because panda throws
        # exception if you check it's truth value:
        # https://pandas.pydata.org/pandas-docs/version/0.15/gotchas.html

        try:
            if s and isinstance(s, list):
                try:
                    DataViewSchema(many=True).load(s)
                except Exception as e:
                    raise Exception(f"Invalid schema list: {e}")
                self._schema = s
            elif s and not isinstance(s, list):
                raise Exception("Schema is not of type list")
        except Exception as e:
            raise Exception(f"Schema is not of type list: {e}")

    def get_input(self):
        """
        Format dict for gql type DataViewInput
        """
        if not hasattr(self, "_schema"):
            self._get_schema_from_uri()

        return {
            k: v
            for k, v in {
                "name": self.name,
                "uri": self.uri,
                "owner_id": self._owner_id,
                "schema": self._schema,
            }.items()
            if v
        }

    def _get_schema_from_uri(self):
        """
        Read first line from csv file read from self.uri as dataframe,
        grab schema from dataframe object, return as list of json:
        {
          type: "string",
          name: "my_col_name"
        }
        """

        def _get_date_cols(dataframe: pd.DataFrame) -> list:
            columns = df.columns
            row_1 = df.iloc[0].values
            date_cols = []

            for i, d in enumerate(row_1):
                if isinstance(d, str) and filter_date(d):
                    date_cols.append(columns[i])

            return date_cols

        try:
            df = pd.read_csv(self.uri, nrows=1)
        except (HTTPError, FileNotFoundError):
            raise Exception("Cannot access data resource")

        date_cols = _get_date_cols(df)
        for date_col in date_cols:
            df[date_col] = pd.to_datetime(df[date_col])

        # Pandas to_json function converts dataframe object to json
        # in doing so it transforms df datatypes into json-like datatypes
        # ---
        # dtypes object -> string
        # dtypes int64 -> integer
        # dtypes float64 -> number
        # dtypes datetime64[ns] -> datetime
        # dtypes category -> any

        self._schema = [
            {"name": s["name"], "schema_type": s["type"]}
            for s in json.loads(df.to_json(orient="table"))
            .get("schema", {})
            .get("fields")
        ]


class DataViewSchema(Schema):
    """
    Schema to validate the schema field on DataViews
    """

    name = fields.Str(required=True)
    schema_type = fields.Str(required=True)
