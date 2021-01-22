# cape-ds

[![codecov](https://codecov.io/gh/capeprivacy/cape-ds/branch/main/graph/badge.svg?token=nimecXcQzo)](https://codecov.io/gh/capeprivacy/cape-ds)

![](./img/logo.png)

The Data Science Library for Cape

### Developing

Initialize a virtual environment. Install dependecies by running:

```sh
$ make bootstrap
```

### Running locally against Coordinator Container

Set the Coordinator URL by exporting the `CAPE_COORDINATOR` environment variable:
```sh
$ export CAPE_COORDINATOR=https://demo.capeprivacy.com
```

You'll need a user token to authenticate requests to the Coordinator API. Generate a new user token via the UI (demo.capeprivacy.com) and pass it to the `login` method defined on the main `Cape` class:
```
from cape import Cape

c = Cape()
c.login(token='token_string_123')
```

### Running Tests

```sh
$ make test
$ make coverage # to see the code coverage report
```
