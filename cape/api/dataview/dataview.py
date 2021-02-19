import json
from abc import ABC
from typing import List
from typing import Union
from urllib.error import HTTPError
from urllib.parse import urlparse

import pandas as pd
from marshmallow import Schema
from marshmallow import fields

from ...utils import filter_date
from ...vars import PANDAS_TO_JSON_DATATYPES


class DataView(ABC):
    """
    Dataview objects keep track of the business logic around datasets.

    Dataviews can be added to projects.
    """

    def __init__(
        self,
        name: str = None,
        uri: str = None,
        owner_id: str = None,
        owner_label: str = None,
        schema: Union[pd.Series, List, None] = None,
        id: str = None,
        location: str = None,
        owner: dict = None,
        user_id: str = None,
    ):
        """
        Initialize the object.

        Arguments:
            name: name of `DataView`.
            uri: URI of `DataView`.
            owner_label: Label of `Organization` that owns this `DataView`
            owner_id: ID of `Organization` that owns this `DataView`
            schema: schema (description of each column's datatype) of the data that `DataView` points to.
            id: Returned ID of `DataView`.
            location: Returned URI of `DataView`.
            owner: Returned dictionary of fields related to the `DataView` owner.
            user_id: User ID of requester.
        """
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self._location: str = location
        self._owner_id: str = owner.get("id") if owner else owner_id
        self._owner_label: str = owner.get("label") if (
            owner and owner.get("label")
        ) else owner_label
        self._user_id: str = user_id
        self.schema: Union[pd.Series, List, None] = schema
        self._owner: dict = owner
        self._cols = None

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, location={self.location})"

    def __getitem__(self, cols):
        if isinstance(cols, str):
            self._cols = [cols]
        elif isinstance(cols, tuple):
            self._cols = [c for c in cols]
        return self

    @property
    def location(self) -> str:
        if not self._location:
            return self.uri or None
        return self.uri or self._location

    @property
    def schema(self) -> dict:
        """
        Return schema as a dict of column names as keys, and values as key data types
        """
        if hasattr(self, "_schema"):
            return {s.get("name"): s.get("schema_type") for s in self._schema}

    @schema.setter
    def schema(self, s: Union[pd.Series, List]):
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
                    jsonify_schema = self._convert_pd_objects_json(s)
                except Exception as e:
                    raise Exception(f"Invalid schema pd.Series: {e}")
                self._schema = jsonify_schema
                return

        raise Exception("Schema is not of type pd.Series")

    def _get_input(self):
        """
        Format dict for gql type DataViewInput
        """

        if not hasattr(self, "_schema") and urlparse(self.uri).scheme in [
            "http",
            "https",
        ]:
            schema = self._get_schema_from_uri()
            self._schema = schema
        elif not hasattr(self, "_schema"):
            raise Exception("DataView schema must be specified.")

        return {
            k: v
            for k, v in {
                "name": self.name,
                "uri": self.uri,
                "owner_id": self._owner_id,
                "owner_label": self._owner_label,
                "schema": self._schema,
            }.items()
            if v
        }

    def _convert_pd_objects_json(self, pd_obj: pd.Series) -> list:
        """
        Accepts a pandas dataframe.dtype, converts this pandas schema to a dictionary of JSON-like
        data types defined by the PANDAS_TO_JSON_DATATYPES. Returns converted schema list.
        """
        json_obj = pd_obj.apply(lambda x: x.name).to_dict()
        schema = [{"name": k, "schema_type": v} for k, v in json_obj.items()]

        for i, s in enumerate(schema):
            schema[i]["schema_type"] = PANDAS_TO_JSON_DATATYPES[s.get("schema_type")]

        return schema

    def _get_schema_from_uri(self) -> list:
        """
        Read first line from csv file read from self.uri as dataframe,
        grab schema from dataframe object, return as list of json:
        {
          type: "string",
          name: "my_col_name"
        }
        """

        def _get_date_cols(dataframe: pd.DataFrame) -> list:
            """
            Get list of column names that are of datetime data types
            """
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

        return [
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
