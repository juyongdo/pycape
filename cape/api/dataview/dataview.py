import json
import pandas as pd
from marshmallow import Schema, fields

from urllib.error import HTTPError

from cape.utils import filter_date
from cape.vars import PANDAS_TO_JSON_DATATYPES


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
        owner_id: str = None,
        user_id: str = None,
        schema: dict = None,
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
        self._owner_id: str = owner.get("id") if owner else owner_id
        self._user_id: str = user_id
        self.schema: pd.Series = schema

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name}, location={self.location})>"

    @property
    def location(self) -> str:
        """
        Protect location property by validating authorized user is the owner of the DataView
        """
        # TODO: make _user and _owner only settable upon initilization
        if self._user_id and self._owner_id and self._user_id == self._owner_id:
            return self.uri or self._location

    @property
    def schema(self) -> dict:
        """
        Return schema as a dict of column names as keys, and values as key data types
        """
        if hasattr(self, "_schema"):
            return {s.get("name"): s.get("schema_type") for s in self._schema}

    @schema.setter
    def schema(self, s):
        """
        Validate that updates to the schema property are pd.Series.
        """
        # Check for truthiness seperately because panda throws
        # exception if you check it's truth value within an comparison operator:
        # https://pandas.pydata.org/pandas-docs/version/0.15/gotchas.html
        try:
            if not s:
                return
            elif isinstance(s, list):
                try:
                    DataViewSchema(many=True).load(s)
                except Exception as e:
                    raise Exception(f"Invalid schema list: {e}")
                self._schema = s
                return

        except ValueError:
            if isinstance(s, pd.Series):
                try:
                    jsonify_schema = self.convert_pd_objects_json(s)
                except Exception as e:
                    raise Exception(f"Invalid schema pd.Series: {e}")
                self._schema = jsonify_schema
                return

        raise Exception("Schema is not of type pd.Series")

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

    def convert_pd_objects_json(self, pd_obj: pd.Series):
        json_obj = pd_obj.apply(lambda x: x.name).to_dict()
        schema = [{"name": k, "schema_type": v} for k, v in json_obj.items()]

        for i, s in enumerate(schema):
            schema[i]["schema_type"] = PANDAS_TO_JSON_DATATYPES[s.get("schema_type")]

        return schema

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
            if s["name"] != "index"
        ]


class DataViewSchema(Schema):
    """
    Schema to validate the schema field on DataViews
    """

    name = fields.Str(required=True)
    schema_type = fields.Str(required=True)
