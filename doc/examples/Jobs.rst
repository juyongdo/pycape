Jobs
==========

Create a job
------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>>
    >>> dataview_1 = my_project.get_dataview(uri="s3://my-data.csv")
    >>> dataview_2 = my_project.get_dataview(uri="s3://my-data.csv")
    >>>
    >>> schema = dataview_2.schema
    >>> print(schema)
    >>> {'transaction_date': 'datetime', 'transaction_amount': 'number'}
    >>>
    >>> job = VerticalLinearRegressionJob(
        x_train=dataview_1['transaction_amount'],
        y_train=dataview_2['transaction_amount'],
        metrics=['r-squared', 'rmse']
    )
    >>>
    >>> my_project.create_job(job=job)
