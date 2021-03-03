import json
from abc import ABC
from typing import Optional
from ...network.requester import Requester


class Task(ABC):
    """
    Tasks contain the instructions for how a Cape worker should run a job.

    Arguments:
        model_output (str): ID of `Project`.
        kwargs (any): 	Keyword arguments to construct a layer.
    """

    def __init__(self, model_output: Optional[str] = None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self._model_output = model_output

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

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
