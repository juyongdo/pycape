Projects
========


List Projects
-------------

.. code-block:: python

    >>> c = Cape()
    >>> c.login()
    
    >>> c.list_projects()

    PROJECT ID   NAME                LABEL
    -----------  ------------------  ------------------
    project_123  Sales Transactions  sales-transactions


Get Project
-----------

.. code-block:: python

    >>> c = Cape()
    >>> c.login()
    
    >>> c.get_project(id="project_123")

    Project(id=project_123, name=cape, label=cape)


Delete a Project
----------------

.. code-block:: python

    >>> c = Cape()
    >>> c.login()
    
    >>> c.remove_project(id="project_123")

    Project (project_123) deleted