from typing import Optional, List, NoReturn

from ...network.requester import Requester
from ...vars import JOB_TYPE_LR
from ..dataview.dataview import DataView
from .task import Task


class VerticallyPartitionedLinearRegression(Task):
    """
    Inherits from: `Task`.

    Contains instructions for encrypted training of linear regression models using \
    vertically-partitioned datasets.

    Vertically-partitioned datasets refer to the joining of columns (i.e. features) from \
    several parties.

    !!!note
        This task expects `DataViews` with floating-point inputs. Internally, values will be \
        re-encoded by the Cape Worker into the \
        [fixed-point numbers](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) necessary \
        for encrypted computation.

    !!!note
        This task expects its input `DataViews` to be aligned by index (although indexing \
        columns need not be present in either of the DataViews or their underlying datasets).

    !!!note
        This task expects its input `DataViews` to have max values scaled between 1.0 and 10.0.

    Currently, input data must be scaled to single digits; for any floating-point vector `c` in \
    the input data views `x` and `y`, `c` must be scaled such that `1.0 <= max(c) < 10.0.` \
    This bound allows the Cape Worker to allocate all of its precision for significant digits \
    throughout the linear regression computation, while still maintaining the guarantee that \
    fixed-point numbers won't overflow. For logarithimically-distributed vectors, we recommend \
    applying a log-transform before scaling to this bound.

    Arguments:
        x_train_dataview (Union[`DataView`, `DataView`List[str]]): `DataView` that points \
        to a dataset that contains training set values.
        y_train_dataview (Union[`DataView`, `DataView`List[str]]): `DataView` that points \
        to a dataset that contains target values.
        model_location (str): The AWS S3 bucket name to which Cape will write the output of the model training.
        model_owner (str): The ID of the organization participating in the computation that will own the
        trained model and it's outputs.
    """

    job_type: Optional[str] = JOB_TYPE_LR

    def __init__(
        self,
        model_location: str,
        model_owner: str,
        x_train_dataview: DataView,
        y_train_dataview: DataView,
        id: Optional[str] = None,
    ):
        self.id: Optional[str] = id
        self.model_location: str = model_location
        self.model_owner: str = model_owner

        self._validate_dataview_parse_cols(x_train_dataview, "x")
        self._validate_dataview_parse_cols(y_train_dataview, "y")

        self._x_train_dataview: DataView = x_train_dataview
        self._y_train_dataview: DataView = y_train_dataview

    def __repr__(self):
        return " ".join(
            f"{self.__class__.__name__}(x_train_dataview={self.x_train_dataview.name}{self._x_train_dataview._cols or ''}, \
            y_train_dataview={self._y_train_dataview.name}{self._y_train_dataview._cols or ''}, \
            model_location={self.model_location}, model_owner={self.model_owner})".split()
        )

    @property
    def model_location(self):
        return super(Task, self).model_location

    @Task.model_location.setter  # noqa: F811
    def model_location(self, location: str):  # noqa: F811
        Task.model_location.fset(self, location)

    @property
    def model_owner(self):
        return super(Task, self).model_owner

    @Task.model_owner.setter  # noqa: F811
    def model_owner(self, owner: str):  # noqa: F811
        Task.model_owner.fset(self, owner)

    @property
    def x_train_dataview(self):
        return self._x_train_dataview

    @x_train_dataview.setter
    def x_train_dataview(self, x_train_dataview: DataView):
        self._validate_dataview_parse_cols(x_train_dataview, "x")
        self._x_train_dataview = x_train_dataview

    @property
    def y_train_dataview(self):
        return self._y_train_dataview

    @y_train_dataview.setter
    def y_train_dataview(self, y_train_dataview: DataView):
        self._validate_dataview_parse_cols(y_train_dataview, "y")
        self._y_train_dataview = y_train_dataview

    @staticmethod
    def _get_dataview_cols(dataview: DataView) -> Optional[List[str]]:
        cols = dataview._cols

        if not cols and dataview.schema:
            cols = list(dataview.schema.keys())
        elif not cols and not dataview.schema:
            return None

        return cols

    def _validate_dataview_parse_cols(self, dataview, dataview_type: str) -> NoReturn:
        missing_params = []

        if not dataview:
            raise Exception(f"{dataview_type} DataView missing")

        if not dataview.id:
            missing_params.append(f"{dataview_type} DataView ID")

        cols = self._get_dataview_cols(dataview)

        if not cols:
            missing_params.append(f"{dataview_type} DataView columns")

        if missing_params:
            raise Exception(f"DataView Missing Properties: {', '.join(missing_params)}")

    def _create_task(self, project_id: str, requester: Requester, timeout: float = 600):
        x_cols = self._get_dataview_cols(self._x_train_dataview)
        y_cols = self._get_dataview_cols(self._y_train_dataview)

        task_config = {
            "dataview_x_id": self._x_train_dataview.id,
            "dataview_y_id": self._y_train_dataview.id,
            "dataview_x_col": x_cols,
            "dataview_y_col": y_cols,
            "model_location": self.model_location,
            "model_owner": self.model_owner,
        }
        return super()._create_task(
            project_id=project_id,
            requester=requester,
            timeout=timeout,
            task_config=task_config,
        )
