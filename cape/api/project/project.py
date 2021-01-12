import json
import pandas as pd

from urllib.error import HTTPError
from marshmallow import Schema, fields

from cape.network.requester import Requester
from cape.api.dataview.dataview import DataView
from cape.api.job.job import Job, VerticalLinearRegressionJob


class Project:
    """
    Projects are the higher order objects that we create DataViews and Jobs on
    """

    def __init__(
        self,
        requester,
        user,
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
        self._user = user
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
        return DataView(user=self._user, **data_view)

    def list_dataviews(self):
        """
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: [:class:`cape.api.dataview.dataview`]
        """

        data_views = self._requester.list_dataviews(project_id=self.id)
        return [DataView(user=self._user, **d) for d in data_views]

    def get_dataview(self, id: str = None, uri: str = None):
        """
        :calls: `query project`
        :param project_id: string
        :param id: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        data_view = self._requester.get_dataview(project_id=self.id, id=id, uri=uri)

        return DataView(user=self._user, **data_view[0]) if data_view else None

    def create_job(self, job: Job):
        """
        :calls: `mutation createTask`
        :param job: :class:`cape.api.job.job`
        :rtype: :class:`cape.api.job.job`
        """
        job = self._requester.create_job(project_id=self.id, task_type=job.name)

        # TODO: create mapping between job name and class type to invoke here
        return VerticalLinearRegressionJob(requester=self._requester, **job)
