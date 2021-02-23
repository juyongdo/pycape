import tempfile
from abc import ABC
from typing import Tuple
from urllib.parse import urlparse

import boto3
import numpy as np

from ...network.requester import Requester


class Job(ABC):
    """
    Job objects keep track of jobs that will be/have been submitted to cape workers.
    """

    def __init__(
        self, id: str, status: dict, task: dict, project_id: str, requester: Requester
    ):
        self.id = id
        self.status = status
        self.project_id = project_id

        if task:
            self.job_type = task.get("type", {})

        if status:
            self.status = status.get("code")

        if requester:
            self._requester = requester

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, job_type={self.job_type}, status={self.status})"

    def _approve_job(self, org_id: str) -> dict:
        return self._requester.approve_job(job_id=self.id, org_id=org_id)

    def get_status(self) -> str:
        """
        Calls GQL `query project.job`.

        Returns:
            A `Job` status string.
        """
        job = self._requester.get_job(
            project_id=self.project_id, job_id=self.id, return_params=""
        )
        return job.get("status", {}).get("code")

    def get_results(self) -> Tuple[np.ndarray, dict]:
        """
        Given the requester's project role and authorization level, returns the trained model's weights and metrics.

        Returns:
            weights: A numpy array.
            metrics: A dictionary of different metric values.
        """
        job_results = self._requester.get_job(
            project_id=self.project_id,
            job_id=self.id,
            return_params="model_metrics { name value }\nmodel_location",
        )

        # gql returns metrics in key/value pairs within an array
        # e.g. [{"name": "mse_result", "value": [1.0]}, {"name": "r_squared", "value": [1.0]]
        # here we map to a more pythonic key, value
        # {
        #   "mse_result": [1.0],
        #   "r_squared": [1.0],
        # }

        gqlMetrics = job_results.get("model_metrics", [])
        metrics = {}
        for m in gqlMetrics:
            metrics[m["name"]] = m["value"]

        location = job_results.get("model_location", None)
        if location is None or location == "":
            return None, metrics

        # pull the bucket info if the regression weights were stored on s3
        # location will look like s3://my-bucket/<job_id>
        p = urlparse(location)
        if p.scheme != "s3":
            raise Exception(f"only s3 locations supported, got {p.scheme}")

        # tell boto3 we are pulling from s3, p.netloc will be the bucket
        b = boto3.resource(p.scheme).Bucket(p.netloc)
        weights_tmp = tempfile.NamedTemporaryFile()

        # save the weights for this job in a temp file
        b.download_file(f"{self.id}/regression_weights", weights_tmp.name)

        # return the weights (decoded to np) & metrics
        return np.loadtxt(weights_tmp.name), metrics
