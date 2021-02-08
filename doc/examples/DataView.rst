DataView
==========


Get list of data views for a project
------------------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> my_project.list_dataviews()

    DATAVIEW ID  NAME    LOCATION                     SCHEMA
    -----------  ------  ---------------------------  ------------------------------------------------------------------------------------
    dataview_1  y-data  https://data.com/y_data.csv  {'transaction_date': 'datetime', 'state': 'string', 'transaction_amount': 'integer'}
    dataview_2  x-data                               {'transaction_date': 'datetime', 'state': 'string', 'transaction_amount': 'integer'}


Get a data view
---------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> # get by id
    >>> my_project.get_dataview(id="dataview_123")
    DataView(id=dataview_123, name=my-data, location=s3://my-data.csv)
    
    >>> # get by uri
    >>> my_project.get_dataview(uri="s3://my-data.csv")
    DataView(id=dataview_123, name=my-data, location=s3://my-data.csv)


Add a data view to a project
----------------------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> data_view = DataView(name="my-data", uri="s3://my-data.csv")
    >>> my_project.add_dataview(data_view)

    DataView(id=abc123, name=my-data, location=s3://my-data.csv)

By default, Cape attempts to look at your data and create a schema. 

By inspecting the schema property, other data scientists that are added as contributors to the current project are able to identify which data columns should be trained against. 

If you would prefer to specify your data's schema yourself, you can do so using the `schema` parameter. DataViews can be instatiated with a pandas series of type `pd.Series`

.. code-block:: python

    >>> import pandas as pd
    >>> df = pd.DataFrame(data={'col_1': [1, 2], 'col_2': [3, 4]})
    >>> df.dtypes

    col1    int64
    col2    int64
    dtype: object

    >>> data_view = DataView(name="my-data", uri="s3://my-data.csv", schema=df.dtypes)
    >>> data_view.schema

    {'col_1': 'integer', 'col_2': 'integer'}

DataViews can also be instantiated as a list of data types. Accepted schema data types include: `string`, `integer`, `number`, `datetime`, `any` 

.. code-block:: python

    >>> schema = [{'name': 'col_1', 'schema_type': 'integer'}, {'name': 'col_2', 'schema_type': 'integer'}]
    >>> data_view = DataView(name="my-data", uri="s3://my-data.csv", schema=schema)
    >>> data_view.schema 

    {'col_1': 'integer', 'col_2': 'integer'}


Delete a DataView
-----------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    
    >>> my_project.remove_dataview(id="dataview_123")

    DataView (dataview_123) deleted


