import json
from cape.vars import JOB_TYPES


class Job:
    """
    Job objects keep track of tasks/jobs that will be/have been submitted to cape workers
    """

    def __init__(self, **kwargs):
        self._requester = kwargs.get("requester")
        # self.job_type = job_type or kwargs.get("job_type")
        # self.id = id
        for k, v in kwargs.items():
            self.__dict__[k] = v

        if not self.job_type:
            raise Exception("Jobs cannot be initialized without a job type")
        elif self.job_type not in JOB_TYPES:
            raise Exception("Job initialized with invalid job type")

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, job_type={self.job_type})>"

    def create_job(self, project_id: str, task_config: dict = None):
        return self._requester.create_job(
            project_id=project_id,
            job_type=self.job_type,
            task_config=json.dumps(task_config) if task_config else None,
        )

    def assign_job_roles(self, job_roles_input):
        return self._requester.assign_job_roles(
            job_id=self.id, job_roles_input=json.dumps(job_roles_input)
        )

    def submit_job(self):
        return self._requester.submit_job(job_id=self.id)