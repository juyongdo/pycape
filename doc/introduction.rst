Introduction
============

The Data Science Library for Cape

(Very short) tutorial
---------------------

To access projects, create a `Cape` instance::

    from cape import Cape

    c = Cape()
    c.login()

    c.list_projects()
    

Get an instance your created `Project` in order conduct project-level level actions such as  creating `DataViews` and submitting `Jobs`:: 
    
    from cape.api.dataview import DataView

    c.get_project(id="project_123")

    data_view = DataView(name="my-data", uri="s3://my-data.csv")
    my_project.add_dataview(data_view)


Download and install
--------------------
TODO

Licensing
---------
TODO

