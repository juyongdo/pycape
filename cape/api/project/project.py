import io
import sys
from abc import ABC
from typing import Dict
from typing import List
from typing import Optional

from tabulate import tabulate

from ...network.requester import Requester
from ...vars import JOB_TYPE_LR
from ..dataview.dataview import DataView
from ..job.job import Job
from ..job.vertical_linear_regression_job import VerticalLinearRegressionJob
from ..organization.organization import Organization


class Project(ABC):
    """
    Projects are business contexts in which we can add DataViews and submit Jobs.

    Multiple organizations can collaborate on one Project.
    """

    def __init__(
        self,
        user_id: str,
        id: Optional[str] = None,
        name: Optional[str] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        owner: Optional[dict] = None,
        organizations: Optional[List[Dict]] = None,
        data_views: Optional[List[Dict]] = None,
        jobs: Optional[List[Dict]] = None,
        requester: Optional[Requester] = None,
        out: Optional[io.StringIO] = None,
    ):
        """
        Initialize the object.

        Arguments:
            user_id: User ID of requester.
            id: ID of `Project`.
            name: name of `Project`.
            label: label of `Project`.
            description: description of `Project`.
            owner: Returned dictionary of fields related to the `Project` owner.
            organizations: Returned list of fields related to the organizations associated with the `Project`.
            data_views: Returned list of `DataViews` added to the `Project`.
            requester: Instance of `Requester` class so that we can chain methods on `Project` class instantiations.
            out: Function to use to write to the interpreter.
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
            self.organizations: List[Organization] = [
                Organization(**o) for o in organizations
            ]

        if data_views is not None:
            self.dataviews: List[DataView] = [DataView(**d) for d in data_views]

        if jobs is not None:
            jobs_temp = []
            for j in jobs:
                job_type = j.get("task", {}).get("type")
                job_class = self._get_job_class(job_type=job_type)
                jobs_temp.append(
                    job_class(
                        job_type=job_type,
                        project_id=self.id,
                        **j,
                        requester=self._requester,
                    )
                )

            self.jobs: List[Job] = jobs_temp

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, label={self.label})"

    @staticmethod
    def _get_job_class(job_type):
        job_type_map = {JOB_TYPE_LR: VerticalLinearRegressionJob}
        return job_type_map.get(job_type)

    def add_org(self, org_id: str):
        """
        Calls GQL `mutation addProjectOrganization`

        Arguments:
            org_id: ID of `Organization`.
        Returns:
            A list of `Project` instances.
        """
        project_org = self._requester.add_project_org(project_id=self.id, org_id=org_id)
        return Project(
            requester=self._requester,
            user_id=self._user_id,
            **project_org.get("Project"),
        )

    def list_dataviews(self) -> List[DataView]:
        """
        Calls GQL `query project.dataviews`

        Returns:
            A list of `DataView` instances.
        """

        data_views = self._requester.list_dataviews(project_id=self.id)
        get_data_view_values = [
            DataView(user_id=self._user_id, **d) for d in data_views
        ]
        dv_ids = []
        dv_names = []
        dv_locations = []
        dv_owners = []

        for dv in get_data_view_values:
            dv_ids.append(dv.id)
            dv_names.append(dv.name)
            dv_locations.append(dv.location)
            dv_owner_label = dv._owner.get("label")
            if self._user_id in [x.get("id") for x in dv._owner.get("members")]:
                dv_owners.append(f"{dv_owner_label} (You)")
            else:
                dv_owners.append(dv_owner_label)

        format_data_views = {
            "DATAVIEW ID": dv_ids,
            "NAME": dv_names,
            "LOCATION": dv_locations,
            "OWNER": dv_owners,
        }
        self._out.write(tabulate(format_data_views, headers="keys") + "\n")
        return [DataView(user_id=self._user_id, **d) for d in data_views]

    def get_dataview(
        self, id: Optional[str] = None, uri: Optional[str] = None
    ) -> DataView:
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

    def add_dataview(self, dataview: DataView) -> DataView:
        """
        Calls GQL `mutation addDataView`

        Arguments:
            dataview: Instance of class `DataView`.
        Returns:
            A `DataView` instance.
        """
        # TODO: validate get_input
        data_view_input = dataview._get_input()
        data_view_dict = self._requester.add_dataview(
            project_id=self.id, data_view_input=data_view_input
        )
        data_view = DataView(user_id=self._user_id, **data_view_dict)

        if hasattr(self, "dataviews"):
            self.dataviews.append(data_view)
        else:
            self.dataviews = [data_view]
        return data_view

    def _create_job(self, job: Job, timeout: float = 600) -> Job:
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
        )._create_job(project_id=self.id, timeout=timeout)
        return job.__class__(
            job_type=job.job_type, **created_job, requester=self._requester,
        )

    def submit_job(self, job: Job, timeout: float = 600) -> Job:
        """
        Calls GQL `mutation createTask`

        Arguments:
            job: Instance of class `Job`.
        Returns:
            A `Job` instance.
        """
        created_job = self._create_job(job, timeout=timeout)

        submitted_job = created_job._submit_job()

        return job.__class__(
            job_type=job.job_type,
            project_id=self.id,
            **submitted_job,
            requester=self._requester,
        )

    def approve_job(self, job: Job, org: Organization) -> Job:
        approved_job = job._approve_job(org.id)

        return job.__class__(
            job_type=job.job_type,
            project_id=self.id,
            **approved_job,
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
        job = self._requester.get_job(project_id=self.id, job_id=id, return_params="")

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

        if hasattr(self, "dataviews"):
            self.dataviews = [x for x in self.dataviews if id != x.id]

        self._out.write(f"DataView ({id}) deleted" + "\n")
        return
