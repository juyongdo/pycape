import json
from cape.api.job.job import Job


class VerticalLinearRegressionJob(Job):
    name = "LINEAR_REGRESSION"
    id = None
    model = None
    x_train = None
    y_train = None
    metrics = None
    validation_data = None

    def assign_job_roles(self, model_owner, data_provider):
        # TODO: Get task roles from project roles
        job_roles = {
            "task_id": self.id,
            "task_type": self.name,
            "model_owner": model_owner,
            "data_provider": data_provider,
        }
        job = super().assign_job_roles(
            job_id=self.id, job_roles_input=json.dumps(job_roles)
        )
        return self(requester=self._requester, **job)

    def submit_job(self):
        return super().submit_job(job_id=self.id)
