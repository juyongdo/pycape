# API Reference

## pycape.Cape 
::: pycape.Cape
    handler: python
    selection:
        members:
            - login
            - list_projects
            - get_project
            - delete_project
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.Project
::: pycape.Project
    handler: python
    selection:
        members:
            - list_dataviews
            - get_dataview
            - create_dataview
            - get_job
            - submit_job
            - delete_dataview
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.Organization
::: pycape.api.organization.organization.Organization
    handler: python
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.DataView
::: pycape.DataView
    handler: python
    selection:
        members:
            - schema
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.Job
::: pycape.Job
    handler: python
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.Task
::: pycape.api.task.task.Task
    handler: python
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## pycape.VerticallyPartitionedLinearRegression
::: pycape.VerticallyPartitionedLinearRegression
    handler: python
    selection:
        filters:
            - "!^_"  # exclude all members starting with _
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false
