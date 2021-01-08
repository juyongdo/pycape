DataView
==========

Add a data view to a project
---------------------------

.. code-block:: python

    >>> c = Cape("abc,123", endpoint="http://cape.com")
    >>> c.login()
    >>> c.add_dataview(project_id="01ET5KHHY11RSVQE20ZEWKQVYC", name="my-data", uri="s3://my-data.csv")
    <DataView ID: abc123>


Get list of data views for a project
------------------------------------

.. code-block:: python

    >>> c = Cape("abc,123", endpoint="http://cape.com")
    >>> c.login()
    >>> c.list_dataviews()
    [{
        "id": "def123",
        "name": "my-dataview",
        "location": "https",
        "schema": [{"name": "col_1", "schema_type": "string"}],
    }]


Get a data view
---------------

.. code-block:: python

    >>> c = Cape("abc,123", endpoint="http://cape.com")
    >>> c.login()
    >>> # get by id
    >>> c.get_dataview(project_id="01ET5KHHY11RSVQE20ZEWKQVYC", id="abc123")
    <DataView ID: abc123>
    >>> # get by uri
    >>> c.get_dataview(project_id="01ET5KHHY11RSVQE20ZEWKQVYC", uri="abc123")
    <DataView ID: abc123>