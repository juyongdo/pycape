import json
from abc import ABC
from urllib.parse import urlparse

from ...exceptions import StorageSchemeException
from ...network.requester import Requester


class Task(ABC):
    """
    Tasks contain the instructions for how a Cape worker should run a job.

    Arguments:
        model_location (str): The AWS S3 bucket name to which Cape will write the output of the model training.
        model_owner (str): The ID of the organization participating in the computation that will own the
        trained model and it's outputs.
    """

    def __init__(self, model_location: str, model_owner: str, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.model_location = model_location
        self.model_owner = model_owner

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, model_owner={self.model_owner})"
        )

    @property
    def model_location(self):
        return self.__model_location

    @model_location.setter
    def model_location(self, model_location: str):
        if not model_location:
            raise Exception("no model location provided")
        self.__model_location = self.validate_s3_location(uri=model_location)

    @property
    def model_owner(self):
        return self.__model_owner

    @model_owner.setter
    def model_owner(self, model_owner: str):
        if not model_owner:
            raise Exception("no model owner provided")
        self.__model_owner = model_owner

    @staticmethod
    def validate_s3_location(uri: str):
        parsed_uri = urlparse(uri)
        if parsed_uri.scheme != "s3":
            raise StorageSchemeException(scheme=parsed_uri.scheme)

        return uri

    def _create_task(
        self,
        project_id: str,
        requester: Requester,
        timeout: float = 600,
        task_config: dict = None,
    ) -> dict:
        task_config["timeout"] = timeout

        return requester.create_job(
            project_id=project_id,
            job_type=self.job_type,
            task_config=json.dumps(task_config) if task_config else None,
        )

    def _submit_job(self, requester: Requester) -> dict:
        return requester.submit_job(job_id=self.id)
