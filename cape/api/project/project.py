from cape.network.requester import Requester
from cape.api.dataview.dataview import DataView
from cape.api.job.job import Job


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
    ):
        """
        :param id: id
        :param name: name
        :param label: label
        :param description: description
        """
        self._requester: Requester = requester
        self._user_id: str = user_id
        self.id: str = id
        self.name: str = name
        self.label: str = label
        self.description: str = description

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

    def create_job(self, job: Job):
        """
        :calls: `mutation createTask`
        :param job: :class:`cape.api.job.job`
        :rtype: :class:`cape.api.job.job`
        """
        created_job = job.__class__(requester=self._requester).create_job(
            project_id=self.id
        )
        return job.__class__(requester=self._requester, **created_job)
