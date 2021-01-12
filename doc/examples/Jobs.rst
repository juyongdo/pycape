Jobs
==========

Create a job
------------

.. code-block:: python

    >>> c = Cape("abc,123", endpoint="http://cape.com")
    >>> c.login()
    >>>
    >>> dataview_1 = cape.get_dataview('s3://my-data.csv')
    >>> dataview_2 = cape.get_dataview('s3://my-data-2.csv')
    >>> schema = dataview_2.schema
    >>> print(schema)
    >>> {'transaction_date': 'datetime', 'transaction_amount': 'float'}
    >>>
    >>> job = VerticalLinearRegressionJob(
        x_train=dataview_1['transaction_amount'],
        y_train=dataview_2['transaction_amount'],
        metrics=['r-squared', 'rmse']
    )
    >>>
    >>> c.create_job(project_id="01ET5KHHY11RSVQE20ZEWKQVYC", job=job)