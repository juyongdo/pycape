import json


class Job:
    """
    Job objects keep track of tasks/jobs that will be/have been submitted to cape workers
    """

    def __init__(self, **kwargs):
        self._requester = kwargs.get("requester")
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def create_job(self, project_id: str, task_config: dict = None):
        return self._requester.create_job(
            project_id=project_id,
            task_type=self.name,
            task_config=json.dumps(task_config) if task_config else None,
        )

    def assign_job_roles(self, job_roles_input):
        return self._requester.assign_job_roles(
            job_id=self.id, job_roles_input=json.dumps(job_roles_input)
        )

    def submit_job(self, job_id):
        return self._requester.submit_job(job_id=job_id)
