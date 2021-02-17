import argparse
import os

import pandas as pd

from cape.api.dataview import DataView
from cape.api.job import VerticalLinearRegressionJob
from cape.cape import Cape

parser = argparse.ArgumentParser(description="Create Job for a given project ID plus other utilities")
parser.add_argument("--token", default=os.environ.get("CAPE_TOKEN"))
parser.add_argument("--project", default=os.environ.get("CAPE_PROJECT"), help="The project ID to create a job on")
parser.add_argument("--coordinator", default=os.environ.get("CAPE_COORDINATOR"))
parser.add_argument("--skip-setup", action="store_true", help="Skips projects setup i.e. adding dataviews")
parser.add_argument("--show-projects", action="store_true", help="Prints projects you are in exits")
args = parser.parse_args()

token = args.token
project_id = args.project
coordinator_url = args.coordinator

if __name__ == '__main__':
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    project = c.get_project(id=project_id)
    j = project.get_job('01EXQ7BYNJXRYDTA6A928GX3NB')
    weights, metrics = j.get_results()
    print('weights', weights)
    print('metrics', metrics)
