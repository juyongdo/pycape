Jobs
==========

Create a job
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
        x_train_dataview=dataview_1,
        x_train_data_cols=['transaction_amount]
        y_train_dataview=dataview_2,
        y_train_data_cols=['transaction_date', 'proprietary_transaction_amount]
    )


Assign Job Roles
----------------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>> 
    >>> my_lr_job = my_project.get_job(id="abc123")
    >>> 
    >>> my_lr_job.assign_job_roles(model_owner="01EW15MK0H8C1CBAVJWP35S6A5", data_provider="01EW15MRW28QAPAMA16DKQEF4W") 
    <VerticalLinearRegressionJob (id=abc123)> 


Submit Job
----------

.. code-block:: python

    >>> c = Cape()
    >>> my_project = c.get_project(id="project_123")
    >>> 
    >>> my_lr_job = my_project.get_job(id="abc123")
    >>> 
    >>> my_lr_job.submit_job() 
    <VerticalLinearRegressionJob (id=abc123)> 