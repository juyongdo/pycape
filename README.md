# pycape

[![codecov](https://codecov.io/gh/capeprivacy/pycape/branch/main/graph/badge.svg?token=nimecXcQzo)](https://codecov.io/gh/capeprivacy/cape-ds)

**pycape** is a set of Python modules for interacting with your Cape data. Using pycape, you can:

- Create and query [dataviews](https://docs.capeprivacy.com/libraries/pycape/reference#pycapedataviews), or pointers to the data that you want to use to train a model using Cape's encrypted learning protocol.
- Submit and track [jobs](https://docs.capeprivacy.com/libraries/pycape/reference#pycapedataviews), which are computational sessions which contain instructions for how to train your model.

Learn more: https://docs.capeprivacy.com/libraries/pycape

## Short Tutorial
Access your Cape projects by creating an instance of the main [`Cape`](https://docs.capeprivacy.com/libraries/pycape/reference#pycapecape) class:
```python
from pycape import Cape

c = Cape()
c.login()

my_projects = c.list_projects()
```

Add `DataViews` to your project, review `DataViews` added by other organizations working in the project, and submit your `Job`.
```python  
from pycape import VerticallyPartitionedLinearRegression

my_project = c.get_project("project_123")
my_project.create_dataview(name="my-data", uri="s3://my-data.csv" owner_label="my-org")

dvs = my_project.list_dataviews()

vlr_job = VerticallyPartitionedLinearRegression(
    train_dataview_x=dvs[0],
    train_dataview_y=dvs[1],
    model_owner="org_123",
)

my_project.submit_job(vlr_job)
```

## Installation

### Prerequisites

* Python 3.6+
* [pip](https://pip.pypa.io/en/stable/installing/)
* [Make](https://www.gnu.org/software/make/) (if installing from source)

### Install via pip
We recommend that you use a [Python "Virtual Environment"](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) when running applications with `pycape`.

Also ensure that your developement enviroment can access the Python Package Index (PyPI) via https.

Once you've activated your virtual enviroment, use pip

```sh
$ pip install pycape
```

### Download from source

Install the library and it's dependencies from git: 

```sh
$ git clone https://github.com/capeprivacy/pycape.git
$ cd pycape
$ make bootstrap
```

## License
Licensed under Apache License, Version 2.0.

See [LICENSE](https://github.com/capeprivacy/cape-python/blob/master/LICENSE) or [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0).


