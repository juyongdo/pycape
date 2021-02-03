Jobs
==========

Submit a job
------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>>
    >>> dataview_1 = my_project.get_dataview(uri="s3://my-data.csv")
    >>> dataview_2 = my_project.get_dataview(uri="s3://my-data-2.csv")
    >>>
    >>> schema_1 = dataview_1.schema
    >>> print(schema_1)
    >>> {'transaction_date': 'datetime', 'transaction_amount': 'number'}
    >>> schema_2 = dataview_2.schema
    >>> print(schema_2)
    >>> {'transaction_date': 'datetime', 'proprietary_transaction_amount': 'number'}
    >>> 
    >>> # define linear regression job
    >>> lr_job = VerticalLinearRegressionJob(
        x_train_dataview=dataview_1["transaction_amount"],
        y_train_dataview=dataview_2["transaction_date", "proprietary_transaction_amount"],
    )
    >>> my_project.submit_job(job=lr_job)
    VerticalLinearRegressionJob(id=abc123)


Get a Job
---------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>>
    >>> my_project.get_job(id="abc123")
    VerticalLinearRegressionJob(id=abc123)
