from typing import Dict, Optional, List

from cape.api.dataview.dataview import DataView
from cape.api.job.job import Job
from cape.api.organization.organization import Organization
from cape.network.requester import Requester


class Project:
    """
    Projects are the higher order objects that we create DataViews and Jobs on
    """

    def __init__(
        self,
        requester: Requester,
        user_id: str,
        id: str = None,
        name: str = None,
        label: str = None,
        description: str = None,
        organizations: List[Dict] = None,
        data_views: List[Dict] = None,
    ):
        """
        :param id: id
        :param name: name
        :param label: label
        :param description: description
        """
        self._requester: Requester = requester
        self._user_id: str = user_id

        if id is None:
            raise Exception("Projects cannot be initialized without an id")

        self.id = id
        self.name: Optional[str] = name
        self.label: Optional[str] = label
        self.description: Optional[str] = description

        if organizations is not None:
            self.organizations: List[Organization] = list(
                map(lambda org_json: Organization(**org_json), organizations)
            )

        if data_views is not None:
            self.dataviews: List[DataView] = list(
                map(lambda dv_json: DataView(**dv_json), data_views)
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name}, label={self.label})>"

    def list_dataviews(self):
        """
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: [:class:`cape.api.dataview.dataview`]
        """

        data_views = self._requester.list_dataviews(project_id=self.id)
        return [DataView(user_id=self._user_id, **d) for d in data_views]

    def get_dataview(self, id: str = None, uri: str = None):
        """
        :calls: `query project`
        :param project_id: string
        :param id: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        data_view = self._requester.get_dataview(project_id=self.id, id=id, uri=uri)

        return DataView(user_id=self._user_id, **data_view[0]) if data_view else None

    def add_dataview(self, dataview: DataView):
        """
        :calls: `mutation addDataView`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: :class:`cape.api.dataview.dataview`
        """
        # TODO: make get_input compatible with DataViews that have been constructed with schemas
        data_view_input = dataview.get_input()
        data_view = self._requester.add_dataview(
            project_id=self.id, data_view_input=data_view_input
        )
        return DataView(user_id=self._user_id, **data_view)

    def create_job(self, job: Job) -> Job:
        """
        :calls: `mutation createTask`
        :param job: :class:`cape.api.job.job`
        :rtype: :class:`cape.api.job.job`
        """

        job_instance = {k: v for k, v in job.__dict__.items()}

        created_job = job.__class__(
            **job_instance, requester=self._requester,
        ).create_job(project_id=self.id)
        return job.__class__(
            job_type=job.job_type, **created_job, requester=self._requester,
        )
