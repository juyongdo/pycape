from typing import Optional

from ...network.requester import Requester
from ...vars import JOB_TYPE_LR
from ..dataview.dataview import DataView
from .task import Task


class VerticallyPartitionedLinearRegression(Task):
    """
    Inherits from: `Task`.

    Contains instructions for training linear regression models using \
    vertically-partitioned datasets.

    Vertically-partitioned datasets refer to the joining of columns (i.e. features) from \
    several parties.

    Arguments:
        x_train_dataview (Union[`DataView`, `DataView`List[str]]): `DataView` that points \
        to a dataset that contains training set values.
        y_train_dataview (Union[`DataView`, `DataView`List[str]]): `DataView` that points \
        to a dataset that contains target values.
        model_location (str): The AWS S3 bucket name to which Cape will write the output of the model training.
    """

    id: Optional[str] = None
    job_type: Optional[str] = JOB_TYPE_LR
    model_location: str = None
    x_train_dataview: DataView = None
    y_train_dataview: DataView = None

    def __repr__(self):
        return " ".join(
            f"{self.__class__.__name__}(x_train_dataview={self.x_train_dataview.name}{self.x_train_dataview._cols or ''}, \
            y_train_dataview={self.y_train_dataview.name}{self.y_train_dataview._cols or ''}, \
            model_location={self.model_location})".split()
        )

    @property
    def model_location(self):
        return super(Task, self).model_location

    @Task.model_location.setter # noqa: F811
    def model_location(self, location):
        Task.model_location.fset(self, location)

    def _create_task(self, project_id: str, requester: Requester, timeout: float = 600):
        def validate_dataview_params(dataview_x, dataview_y):
            missing_params = []
            x_cols = dataview_x._cols
            y_cols = dataview_y._cols

            if not dataview_x.id:
                missing_params.append("X DataView ID")

            if not dataview_y.id:
                missing_params.append("Y DataView ID")

            if not x_cols and dataview_x.schema:
                x_cols = list(dataview_x.schema.keys())
            elif not x_cols and not dataview_x.schema:
                missing_params.append("X DataView columns")

            if not y_cols and dataview_y.schema:
                y_cols = list(dataview_y.schema.keys())
            elif not y_cols and not dataview_y.schema:
                missing_params.append("Y DataView columns")

            return (
                {
                    "x_id": dataview_x.id,
                    "y_id": dataview_y.id,
                    "x_cols": x_cols,
                    "y_cols": y_cols,
                },
                missing_params,
            )

        values, err = validate_dataview_params(
            dataview_x=self.x_train_dataview, dataview_y=self.y_train_dataview
        )

        if err:
            raise Exception(f"DataView Missing Properties: {', '.join(err)}")

        task_config = {
            "dataview_x_id": values.get("x_id"),
            "dataview_y_id": values.get("y_id"),
            "dataview_x_col": values.get("x_cols"),
            "dataview_y_col": values.get("y_cols"),
            "model_location": self.model_location,
        }
        return super()._create_task(
            project_id=project_id,
            requester=requester,
            timeout=timeout,
            task_config=task_config,
        )
