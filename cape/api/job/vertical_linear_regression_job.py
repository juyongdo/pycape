from cape.api.job.job import Job
from cape.vars import JOB_STATUS_CREATED
from cape.vars import JOB_TYPE_LR


class VerticalLinearRegressionJob(Job):
    job_type = JOB_TYPE_LR
    id = None
    status = {"code": JOB_STATUS_CREATED}
    x_train_dataview = None
    x_train_data_cols = None
    y_train_dataview = None
    y_train_data_cols = None

    def create_job(self, project_id: str):
        def validate_params(dataview_x, dataview_y):
            missing_params = []

            if not dataview_x.id:
                missing_params.append("X DataView ID")

            if not dataview_y.id:
                missing_params.append("Y DataView ID")

            if not dataview_x._cols:
                missing_params.append("X DataView columns")

            if not dataview_y._cols:
                missing_params.append("Y DataView columns")

            return (
                {
                    "x_id": dataview_x.id,
                    "y_id": dataview_y.id,
                    "x_cols": dataview_x._cols,
                    "y_cols": dataview_y._cols,
                },
                missing_params,
            )

        values, err = validate_params(
            dataview_x=self.x_train_dataview, dataview_y=self.y_train_dataview
        )

        if err:
            raise Exception(f"DataView Missing Properties: {', '.join(err)}")

        task_config = {
            "dataview_x_id": values.get("x_id"),
            "dataview_y_id": values.get("y_id"),
            "dataview_x_col": values.get("x_cols"),
            "dataview_y_col": values.get("y_cols"),
        }
        return super().create_job(project_id=project_id, task_config=task_config)

    def _submit_job(self):
        return super()._submit_job()

    def get_status(self):
        return super().get_status()
