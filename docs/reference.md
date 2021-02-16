# API Reference

## Cape
::: cape.api.cape.cape.Cape
    handler: python
    selection:
        filters:
            - "!^_"  # exlude all members starting with _
            - "^__init__$"  # but always include __init__ modules and methods
    rendering:
      show_root_heading: false
      show_source: false
      show_root_toc_entry: false

## Project
::: cape.api.project.project.Project
    handler: python
    selection:
        members:
            - list_dataviews
            - get_dataview
            - add_dataview
            - get_job
            - submit_job
            - remove_dataview
    rendering:
      show_root_heading: false
      show_source: false
      show_root_toc_entry: false

## DataView
::: cape.api.dataview.dataview.DataView
    handler: python
    selection:
        members:
            - __init__
    rendering:
      show_root_heading: false
      show_source: false
      show_root_toc_entry: false

## Job
::: cape.api.job.job.Job
    handler: python
    selection:
        members:
            - get_status
            - get_results
    rendering:
      show_root_heading: false
      show_source: false
      show_root_toc_entry: false

## VerticalLinearRegressionJob
::: cape.api.job.vertical_linear_regression_job.VerticalLinearRegressionJob
    handler: python
    selection:
        filters:
            - "!^_"  # exlude all members starting with _
            - "^__init__$"  # but always include __init__ modules and methods
    rendering:
      show_root_heading: false
      show_source: false
      show_root_toc_entry: false