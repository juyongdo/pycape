from cape.api.job.job import Job
from cape.vars import JOB_TYPE_LR


class VerticalLinearRegressionJob(Job):
    job_type = JOB_TYPE_LR
    id = None
    x_train_dataview = None
    x_train_data_cols = None
    y_train_dataview = None
    y_train_data_cols = None
    computation = None

    def create_job(self, project_id: str):
        task_config = {
            "dataview_x_id": self.x_train_dataview.id,
            "dataview_y_id": self.y_train_dataview.id,
            "dataview_x_col": self.x_train_data_cols,
            "dataview_y_col": self.y_train_data_cols,
        }
        return super().create_job(project_id=project_id, task_config=task_config)

    def _submit_job(self):
        return super()._submit_job()

    def get_status(self):
        return super().get_status()
