import json
import tempfile

import boto3
import numpy as np
from typing import Optional

from cape.network.requester import Requester
from cape.vars import JOB_TYPES


class Job:
    """
    Job objects keep track of tasks/jobs that will be/have been submitted to cape workers
    """

    job_type: Optional[str]
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

    def create_job(self, project_id: str, task_config: dict = None) -> dict:
        return self._requester.create_job(
            project_id=project_id,
            job_type=self.job_type,
            task_config=json.dumps(task_config) if task_config else None,
        )

    def _submit_job(self) -> dict:
        return self._requester.submit_job(job_id=self.id)

    def get_status(self) -> str:
        job = self._requester.get_job(
            project_id=self.project_id, job_id=self.id, return_params="status { code }"
        )
        return job.get("status", {}).get("code")

    def get_results(self):
        # job_metrics = self._requester.get_job(
        #     project_id=self.project_id,
        #     job_id=self.id,
        #     return_params="model_metrics { name value }",
        # )
        # # TODO: return model weights
        # return None, job_metrics.get("model_metrics", {})

        b = boto3.resource("s3").Bucket('cape-worker')
        mse_tmp = tempfile.NamedTemporaryFile()
        rsquared_tmp = tempfile.NamedTemporaryFile()
        weights_tmp = tempfile.NamedTemporaryFile()
        b.download_file(f'{self.id}/mse_result', mse_tmp.name)
        b.download_file(f'{self.id}/r_squared_result', rsquared_tmp.name)
        b.download_file(f'{self.id}/regression_weights', weights_tmp.name)

        return np.loadtxt(weights_tmp.name), {
            "mse_result": np.loadtxt(mse_tmp.name),
            "r_squared_result": np.loadtxt(rsquared_tmp.name)
        }


