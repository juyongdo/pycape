Cape Main Class
===============

Login
-----

.. code-block:: python

    >>> c = Cape()
    >>> c.login(token="abc,123", endpoint="http://cape.com")

    Login successful

It is also possible to set your Auth Token and Coordinator endpoint via the environment variables `CAPE_TOKEN` and `CAPE_COORDINATOR`.

.. code-block:: python

    # Call the login method after exporting CAPE_TOKEN and CAPE_COORDINATOR.
    >>> c = Cape()
    >>> c.login()

    Login successful