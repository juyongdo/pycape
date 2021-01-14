from cape.api.job.job import Job


class MultiplicationJob(Job):
    name = "MULTIPLICATION"
    id = None
    computation = None
    project = None
    status = None

    def create_job(self, project_id):
        return super().create_job(project_id=project_id)

    def assign_job_roles(self, job_roles_input: dict):
        job_roles = {
            "task_id": self.id,
            "task_type": self.name,
            "inputter0": job_roles_input.get("inputter0"),
            "inputter1": job_roles_input.get("inputter1"),
        }
        job = super().assign_job_roles(job_roles_input=job_roles)
        return self.__class__(requester=self._requester, **job)

    def submit_job(self):
        job = super().submit_job(job_id=self.id)
        return self.__class__(requester=self._requester, **job)
