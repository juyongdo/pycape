DataView
==========

Add a dataView to a project
---------------------------

.. code-block:: python

    >>> c = Cape("abc,123", endpoint="http://cape.com")
    >>> c.login()
    >>> c.add_dataview(project_id="01ET5KHHY11RSVQE20ZEWKQVYC", name="my-data", uri="s3://my-data.csv")
    <DataView ID: abc123>