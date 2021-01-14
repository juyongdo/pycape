from cape.api.job.job import Job


class MultiplicationJob(Job):
    job_type = "MULTIPLICATION"
    id = None
    computation = None
    project = None
    status = None

    def create_job(self, project_id: str):
        return super().create_job(project_id=project_id)

    def assign_job_roles(self, inputter0: str, inputter1: str):
        job_roles = {
            "task_id": self.id,
            "task_type": self.job_type,
            "inputter0": inputter0,
            "inputter1": inputter1,
        }
        job = super().assign_job_roles(job_roles_input=job_roles)
        return self.__class__(requester=self._requester, **job)

    def submit_job(self):
        job = super().submit_job()
        return self.__class__(requester=self._requester, **job)
