class Job:
    """
    Job objects keep track of tasks/jobs that will be/have been submitted to cape workers
    """

    def __init__(self, requester, **kwargs):
        self._requester = requester
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def assign_job_roles(self, job_id, job_roles_input):
        return self._requester.assign_job_roles(
            job_id=job_id, job_roles_input=job_roles_input
        )

    def submit_job(self, job_id):
        return self._requester.submit_job(job_id=job_id)
