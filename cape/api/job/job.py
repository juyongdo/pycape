import json
import tempfile
import boto3
import numpy as np
from typing import Optional, Tuple
from urllib.parse import urlparse
from abc import ABC

from ...network.requester import Requester
from ...vars import JOB_TYPES


class Job(ABC):
    """
    Jobs track the status and eventually report the results of computation sessions run on Cape workers.
    """

    job_type: str
    id: Optional[str]

    def __init__(self, requester: Requester = None, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        if requester:
            self._requester = requester

        if not self.job_type:
            raise Exception("Jobs cannot be initialized without a job type")
        elif self.job_type not in JOB_TYPES:
            raise Exception("Job initialized with invalid job type")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, job_type={self.job_type}, status={self.status.get('code')})"

    def _create_job(
        self, project_id: str, timeout: float = 600, task_config: dict = None
    ) -> dict:
        task_config["timeout"] = timeout

        return self._requester.create_job(
            project_id=project_id,
            job_type=self.job_type,
            task_config=json.dumps(task_config) if task_config else None,
        )

    def _submit_job(self) -> dict:
        return self._requester.submit_job(job_id=self.id)

    def get_status(self) -> str:
        """
        Query the current status of the Cape `Job`.

        Returns:
            A `Job` status string.

        ** Status Types:**
        
        Status | Desciption
        ------ | ----------
        **`Initialized`** | Job has been intialized.
        **`NeedsApproval`** | Job is awaiting approval by at least one party.
        **`Approved`** | Job has been approved, the computation will commence.
        **`Rejected`** | Job has been rejected, the computation will not run.
        **`Started`** | Job has started.
        **`Completed`** | Job has completed.
        **`Stopped`** | Job has been stopped.
        **`Error`** | Error in running Job.
        """
        job = self._requester.get_job(
            project_id=self.project_id, job_id=self.id, return_params="status { code }"
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
