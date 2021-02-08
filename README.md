# cape-ds

[![codecov](https://codecov.io/gh/capeprivacy/cape-ds/branch/main/graph/badge.svg?token=nimecXcQzo)](https://codecov.io/gh/capeprivacy/cape-ds)

![](./img/logo.png)

The Data Science Library for Cape

### Developing

Initialize a virtual environment. Install dependecies by running:

```sh
$ make bootstrap
```

### Local Development

You'll need a user token to authenticate requests to the Coordinator API. Generate a new user token via the UI (demo.capeprivacy.com)

Set the Coordinator URL by exporting the `CAPE_COORDINATOR` environment variable, and your user token by exporting the `CAPE_TOKEN` environment variable:
```sh
$ export CAPE_COORDINATOR=https://demo.capeprivacy.com
$ export CAPE_TOKEN=abc,123
```

### Quick Tutorial
To access projects, create a `Cape` instance:
```
from cape import Cape

c = Cape()
c.login()

c.list_projects()
```

Get an instance your created `Project` in order conduct project-level level actions such as  creating `DataViews` and submitting `Jobs`: 
```
from cape.api.dataview import DataView

c.get_project(id="project_123")

data_view = DataView(name="my-data", uri="s3://my-data.csv")
my_project.add_dataview(data_view)
```

### Running Tests

```sh
$ make test
$ make coverage # to see the code coverage report
```

### Build Documenation

```sh
$ pip install -U Sphinx
$ sphinx-build -b html doc _build # to build documenation frontend in _build dir
```