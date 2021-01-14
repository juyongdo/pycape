from cape.api.job.job import Job


class VerticalLinearRegressionJob(Job):
    job_type = "LINEAR_REGRESSION"
    id = None
    x_train_dataview = None
    x_train_data_cols = None
    y_train_dataview = None
    y_train_data_cols = None
    computation = None

    def create_job(self, project_id):
        task_config = {
            "dataview_x_id": self.x_train_dataview.id,
            "dataview_y_id": self.y_train_dataview.id,
            "dataview_x_col": self.x_train_data_cols,
            "dataview_y_col": self.y_train_data_cols,
        }
        return super().create_job(project_id=project_id, task_config=task_config)

    def assign_job_roles(self, model_owner, data_provider):
        job_roles = {
            "task_id": self.id,
            "task_type": self.job_type,
            "model_owner": model_owner,
            "data_provider": data_provider,
        }
        job = super().assign_job_roles(job_roles_input=job_roles)
        return self(requester=self._requester, **job)

    def submit_job(self):
        job = super().submit_job()
        return self.__class__(requester=self._requester, **job)
