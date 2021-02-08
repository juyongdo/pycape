Projects
========


List Projects
-------------

.. code-block:: python

    >>> c = Cape()
    >>> c.login()
    
    >>> c.list_projects()
    PROJECT ID                  NAME                LABEL
    --------------------------  ------------------  ------------------
    01EXFE5TK3HJYDX50M85W2QQS1  Sales Transactions  sales-transactions


Get Project
-----------

.. code-block:: python

    >>> c = Cape()
    >>> c.login()
    
    >>> c.get_project(id="01EVS2MV3TEXQ04EPQ97F6CS50")
    Project(id=01EVS2MV3TEXQ04EPQ97F6CS50, name=cape, label=cape)