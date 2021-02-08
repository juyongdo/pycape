DataView
==========


Get list of data views for a project
------------------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> my_project.list_dataviews()
    DATAVIEW ID                 NAME    LOCATION                                   SCHEMA
    --------------------------  ------  -----------------------------------------  ------------------------------------------------------------------------------------
    01EXFR6K4D2HN7B24DGAKP8D6Y  y-data  https://storage.googleapis.com/y_data.csv  {'transaction_date': 'datetime', 'state': 'string', 'transaction_amount': 'integer'}
    01EXFJKQRN3TQ5EQXJAQ9EPCQ6  x-data                                             {'transaction_date': 'datetime', 'state': 'string', 'transaction_amount': 'integer'}


Get a data view
---------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> # get by id
    >>> my_project.get_dataview(id="abc123")
    DataView(id=abc123)
    
    >>> # get by uri
    >>> my_project.get_dataview(uri="abc123")
    DataView(id=abc123)



Add a data view to a project
----------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> data_view = DataView(name="m-data", uri="s3://my-data.csv")
    >>> my_project.add_dataview(data_view)
    DataView(id=abc123)
    
    >>> # pass your own schema to your DataView
    >>> # DataViews can be instatiated with a pandas series of type pd.Series
    >>> import pandas as pd
    >>> df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
    >>> df.dtypes
    col1    int64
    col2    int64
    dtype: object
    >>> data_view = DataView(name="m-data", uri="s3://my-data.csv", schema=df.dtypes)
    
    >>> # DataViews can also be instantiated as a list of data types:
    >>> schema = [{'name': 'col1', 'schema_type': 'integer', 'name': 'col2', 'schema_type': 'interger'}]
    >>> data_view = DataView(name="m-data", uri="s3://my-data.csv", schema=schema)
    >>> # accepted schema data types: string, integer, number, datetime, any 
