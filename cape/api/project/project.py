import sys
from typing import Dict
from typing import List
from typing import Optional

from tabulate import tabulate

from cape.api.dataview.dataview import DataView
from cape.api.job.job import Job
from cape.api.job.vertical_linear_regression_job import VerticalLinearRegressionJob
from cape.api.organization.organization import Organization
from cape.network.requester import Requester
from cape.vars import JOB_TYPE_LR


class Project:
    """
    Projects are the higher order objects that we create DataViews and Jobs on
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
        out = sys.stdout,
    ):
        """
        :param id: id
        :param name: name
        :param label: label
        :param description: description
        """
        self._requester: Requester = requester
        self._user_id: str = user_id
        self._out = out

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
        :calls: `query project`
        :param project_id: string
        :param name: string
        :param uri: string
        :rtype: [:class:`cape.api.dataview.dataview`]
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

    def _create_job(self, job: Job) -> Job:
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

    def submit_job(self, job: Job) -> Job:
        """
        :calls: `query project.job`
        :param id: string
        :rtype: :class:`cape.api.job.Job`
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
        :calls: `query project.job`
        :param id: string
        :rtype: :class:`cape.api.job.Job`
        """
        job = self._requester.get_job(
            project_id=self.id, job_id=id, return_params="status { code } task { type }"
        )

        job_type = job.get("task", {}).get("type")

        job_class = self._get_job_class(job_type=job_type)

        return job_class(
            job_type=job_type, **job, project_id=self.id, requester=self._requester,
        )

    def remove_dataview(self, id: str, out=sys.stdout) -> str:
        """
        :calls: `mutation removeDataView`
        :param id: string
        :rtype: string
        """
        self._requester.remove_dataview(id=id)
        return out.write(f"DataView ({id}) deleted" + "\n")
