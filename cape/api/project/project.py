import io
import sys
from typing import Dict, List, Optional
from abc import ABC
from tabulate import tabulate

from ..dataview.dataview import DataView
from ..job.job import Job
from ..job.vertical_linear_regression_job import VerticalLinearRegressionJob
from ..organization.organization import Organization
from ...network.requester import Requester
from ...vars import JOB_TYPE_LR


class Project(ABC):
    """
    Projects are business contexts in which we can add DataViews and submit Jobs.

    Multiple organizations can collaborate on one Project.
    """

    def __init__(
        self,
        user_id: str,
        id: str = None,
        name: str = None,
        label: str = None,
        description: str = None,
        owner: str = None,
        organizations: List[Dict] = None,
        data_views: List[Dict] = None,
        requester: Requester = None,
        out: io.StringIO = None,
    ):
        """
        Initialize the object.

        Arguments:
            user_id: User ID of requester.
            id: ID of `Project`.
            name: name of `Project`.
            label: label of `Project`.
            description: description of `Project`.
        """
        self._requester: Requester = requester
        self._user_id: str = user_id
        self._out: io.StringIO = out
        if out is None:
            self._out = sys.stdout

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
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, label={self.label})"

    @staticmethod
    def _get_job_class(job_type):
        job_type_map = {JOB_TYPE_LR: VerticalLinearRegressionJob}
        return job_type_map.get(job_type)

    def add_org(self, org_id: str):
        """
        :calls: `mutation addProjectOrganization`
        :param project_id: string
        :param org_id: string
        :rtype: [:class:`cape.api.project.Project`]
        """
        project_org = self._requester.add_project_org(project_id=self.id, org_id=org_id)
        return Project(
            requester=self._requester,
            user_id=self._user_id,
            **project_org.get("Project"),
        )

    def list_dataviews(self):
        """
        Calls GQL `query project.dataviews`
        Returns:
            A list of `DataView` instances.
        """

        data_views = self._requester.list_dataviews(project_id=self.id)
        get_data_view_values = [
            DataView(user_id=self._user_id, **d) for d in data_views
        ]
        format_data_views = {
            "DATAVIEW ID": [x.id for x in get_data_view_values],
            "NAME": [x.name for x in get_data_view_values],
            "LOCATION": [
                x.location for x in get_data_view_values if x._validate_owner()
            ],
            "SCHEMA": [x.schema for x in get_data_view_values],
        }
        return self._out.write(tabulate(format_data_views, headers="keys") + "\n")

    def get_dataview(self, id: Optional[str] = None, uri: Optional[str] = None):
        """
        Calls GQL `query project.dataview`
        Arguments:
            id: ID of `DataView`.
            uri: Unique `DataView` URI.
        Returns:
            A `DataView` instance.
        """
        data_view = self._requester.get_dataview(
            project_id=self.id, dataview_id=id, uri=uri
        )

        return DataView(user_id=self._user_id, **data_view[0]) if data_view else None

    def add_dataview(self, dataview: DataView):
        """
        Calls GQL `mutation addDataView`
        Arguments:
            dataview: Instance of class `DataView`.
        Returns:
            A `DataView` instance.
        """
        # TODO: validate get_input
        data_view_input = dataview.get_input()
        data_view = self._requester.add_dataview(
            project_id=self.id, data_view_input=data_view_input
        )
        return DataView(user_id=self._user_id, **data_view)

    def _create_job(self, job: Job) -> Job:
        """
        Calls GQL `mutation createTask`
        Arguments:
            dataview: Instance of class `Job`.
        Returns:
            A `Job` instance.
        """

        job_instance = {k: v for k, v in job.__dict__.items()}

        created_job = job.__class__(
            **job_instance, requester=self._requester,
        ).create_job(project_id=self.id)
        return job.__class__(
            job_type=job.job_type, **created_job, requester=self._requester,
        )

    def submit_job(self, job: Job) -> Job:
        """
        Calls GQL `mutation createTask`
        Arguments:
            dataview: Instance of class `Job`.
        Returns:
            A `Job` instance.
        """
        created_job = self._create_job(job)

        submitted_job = created_job._submit_job()

        return job.__class__(
            job_type=job.job_type,
            project_id=self.id,
            **submitted_job,
            requester=self._requester,
        )

    def get_job(self, id: str) -> Job:
        """
        Calls GQL `query project.job`
        Arguments:
            id: ID of `Job`.
        Returns:
            A `Job` instance.
        """
        job = self._requester.get_job(
            project_id=self.id, job_id=id, return_params="status { code } task { type }"
        )

        job_type = job.get("task", {}).get("type")

        job_class = self._get_job_class(job_type=job_type)

        return job_class(
            job_type=job_type, **job, project_id=self.id, requester=self._requester,
        )

    def remove_dataview(self, id: str) -> str:
        """
        Calls GQL `mutation removeDataView`
        Arguments:
            id: ID of `DataView`.
        Returns:
            A success messsage write out.
        """
        self._requester.remove_dataview(id=id)
        return self._out.write(f"DataView ({id}) deleted" + "\n")
