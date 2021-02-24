import io
import sys
from abc import ABC
from typing import Optional

from tabulate import tabulate

from ...network.requester import Requester
from ..project.project import Project


class Cape(ABC):
    """
    This is the main class you instantiate to access the Cape DS API.

    Use to authenticate with the Cape Cloud and manage top-level resources such as `Project`.
    """

    def __init__(self, out: io.StringIO = None, endpoint: Optional[str] = None) -> None:
        """
        Arguments:
            out: The interpreter to be written to.
            endpoint: Coordinator endoint to point to.
        """
        self.__requester: Requester = Requester(endpoint=endpoint)
        self.__user_id: str = None
        self._out: io.StringIO = out
        if out is None:
            self._out = sys.stdout

    def login(self, token: Optional[str] = None) -> str:
        """
        Calls `POST /v1/login`. Authenticate with Cape Cloud in order to make subsequent requests.

        Arguments:
            token:  User authentication token.
        Returns:
            A success messsage write out.
        """
        self.__user_id = self.__requester.login(token=token)
        self._out.write("Login successful\n")
        return

    def list_projects(self) -> str:
        """
        Returns all list of projects that requesting user is a contributor of.

        Returns:
            A list of `Project` instances.
        """
        projects = self.__requester.list_projects()
        get_project_values = [Project(user_id=self.__user_id, **p) for p in projects]
        format_projects = {
            "PROJECT ID": [x.id for x in get_project_values],
            "NAME": [x.name for x in get_project_values],
            "LABEL": [x.label for x in get_project_values],
        }
        self._out.write(tabulate(format_projects, headers="keys") + "\n")
        return [
            Project(requester=self.__requester, user_id=self.__user_id, **p)
            for p in projects
        ]

    def get_project(
        self, id: Optional[str] = None, label: Optional[str] = None
    ) -> Project:
        """
        Query a `Project` by either ID or label.

        Returns:
            A list of `Project` instances.

        Arguments:
            id: ID of `Project`.
            label: Unique `Project` label.
        Returns:
            A `Project` instance.
        """
        project = self.__requester.get_project(id=id, label=label)
        return Project(requester=self.__requester, user_id=self.__user_id, **project)

    def create_project(
        self, name: str, owner: str, description: Optional[str] = None
    ) -> Project:
        """
        Calls GQL `mutation createProject`

        Arguments:
            name: name of project.
            owner: ID of `Organization` this project should belong to.
            description: description of project.
        Returns:
            A `Project` instance.
        """
        project = self.__requester.create_project(
            name=name, owner=owner, description=description
        )
        return Project(requester=self.__requester, user_id=self.__user_id, **project)

    def delete_project(self, id: str) -> str:
        """
        Delete a `Job` by ID.

        Arguments:
            id: ID of `Project`.
        Returns:
            A success messsage write out.
        """
        self.__requester.archive_project(id=id)
        return self._out.write(f"Project ({id}) deleted" + "\n")
