# API Reference

## cape.Cape 
::: cape.Cape
    handler: python
    selection:
        filters:
            - "!^_"  # exlude all members starting with _
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## cape.Project
::: cape.Project
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
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## cape.DataView
::: cape.DataView
    handler: python
    selection:
        members:
            - "!^_"  # exlude all members starting with _
            - "!"  # exlude all members starting with _
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## cape.Job
::: cape.Job
    handler: python
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false

## cape.VerticallyPartitionedLinearRegression
::: cape.VerticallyPartitionedLinearRegression
    handler: python
    selection:
        filters:
            - "!^_"  # exlude all members starting with _
    rendering:
        heading_level: 4
        show_root_heading: false
        show_source: false
        show_root_toc_entry: false