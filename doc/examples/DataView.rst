DataView
==========

Add a data view to a project
---------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>> 
    >>> my_project.add_dataview(name="my-data", uri="s3://my-data.csv")
    <DataView ID: abc123>


Get list of data views for a project
------------------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>>
    >>> my_project.list_dataviews()
    [
        <DataView ID: 01EVS2NE325SETZKF1MJEVXK00>,
        <DataView ID: 01EVSKC1BZW9B5QGH7KHDW8RQ3>,
        <DataView ID: 01EVSWX4ZY5QE9PSN8GNJBMAWN>
    ]


Get a data view
---------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>>
    >>> # get by id
    >>> my_project.get_dataview(id="abc123")
    <DataView ID: abc123>
    >>>
    >>> # get by uri
    >>> my_project.get_dataview(uri="abc123")
    <DataView ID: abc123>