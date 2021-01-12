import json
import pandas as pd
from urllib.error import HTTPError
from marshmallow import Schema, fields
from cape.network.requester import Requester
from cape.api.dataview.dataview import DataView
from IPython import embed


class Project:
    """
    Projects are the higher order objects that we create DataViews and Jobs on
    """

    def __init__(
        self,
        requester,
        id: str = None,
        name: str = None,
        label: str = None,
        description: str = None,
    ):
        """
        :param id: id
        :param name: name
        :param label: label
        :param description: description
        """
        self._requester = requester
        self.id: str = id
        self.name: str = name
        self.label: str = label
        self.description: str = description

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name}, label={self.label})>"

    def add_dataview(self, name: str, uri: str, owner_id: str = None):
        """
        :calls: `mutation addDataView`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        dv = DataView(name=name, uri=uri, owner_id=owner_id)
        data_view_input = dv.get_input()
        data_view = self._requester.add_dataview(
            project_id=self.id, data_view_input=data_view_input
        )
        return DataView(**data_view)

    def list_dataviews(self):
        """
        Queries gql for list of dataviews by project
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: [:class:`cape.api.dataview.dataview`]
        """

        data_views = self._requester.list_dataviews(project_id=self.id)
        return [DataView(**d) for d in data_views]

    def get_dataview(self, id: str = None, uri: str = None):
        """
        Queries gql for list of dataviews by project
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: [:class:`cape.api.dataview.dataview`]
        """
        data_view = self._requester.get_dataview(project_id=self.id, id=id, uri=uri)

        return DataView(**data_view[0]) if data_view else None
