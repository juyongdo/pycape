import argparse
import os
import sys
import time

import pandas as pd

from pycape import Cape
from pycape import DataView
from pycape import VerticallyPartitionedLinearRegression

parser = argparse.ArgumentParser(
    description="Create Job for a given project ID plus other utilities"
)
parser.add_argument("--token", default=os.environ.get("CAPE_TOKEN"))
parser.add_argument(
    "--project",
    default=os.environ.get("CAPE_PROJECT"),
    help="The project ID to create a job on",
)
parser.add_argument("--coordinator", default=os.environ.get("CAPE_COORDINATOR"))
parser.add_argument(
    "--skip-setup",
    action="store_true",
    help="Skips projects setup i.e. adding dataviews",
)
parser.add_argument(
    "--skip-approval",
    action="store_true",
    help="Skips auto-approving the jobs",
)
parser.add_argument(
    "--show-projects", action="store_true", help="Prints projects you are in exits"
)
parser.add_argument(
    "--timeout", default=90, type=int, help="How long to wait for the computation to finish"
)
parser.add_argument(
    "--bucket", default="cape-worker", type=str, help="Which S3 bucket to use"
)
args = parser.parse_args()

token = args.token
project_id = args.project
coordinator_url = args.coordinator
bucket = args.bucket


def list_projects():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    print("projects")
    c.list_projects()


def get_project():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    project = c.get_project(id=project_id)
    print(project)
    print("\nOrgs:")
    for o in project.organizations:
        print(f"\t{o}")

    print("\nData Views:")
    for dv in project.dataviews:
        print(f"\t{dv}")


def setup_project():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)

    project = c.get_project(id=project_id)
    print("linear-regression-project")
    print(f"\t{project}")
    print("orgs", project.organizations)

    x_schema = [
        {"name": "x_1", "schema_type": "numeric"},
        {"name": "x_2", "schema_type": "numeric"},
        {"name": "x_3", "schema_type": "numeric"},
    ]
    y_schema = [{"name": "y", "schema_type": "numeric"}]
    org_dv = {
        project.organizations[0].name: {
            "uri": f"s3://{bucket}/x_data_cape_demo.csv",
            "schema": x_schema,
        },
        project.organizations[1].name: {
            "uri": f"s3://{bucket}/y_data_cape_demo.csv",
            "schema": y_schema,
        },
    }

    for org in project.organizations:
        try:
            print(
                project.create_dataview(
                    name=f"{org.name}-data",
                    owner_id=org.id,
                    uri=org_dv[org.name]["uri"],
                    schema=org_dv[org.name]["schema"],
                )
            )
        except KeyError:
            continue


def make_job():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    project = c.get_project(id=project_id)
    print(project)
    print("\nOrgs:")
    for o in project.organizations:
        print(f"\t{o}")

    print("\nData Views:")
    for dv in project.dataviews:
        print(f"\t{dv}")

    job = VerticallyPartitionedLinearRegression(
        x_train_dataview=project.dataviews[0]["x_1"],
        y_train_dataview=project.dataviews[1]["y"],
        model_location=f"s3://{bucket}",
        model_owner=project.organizations[0].id
    )

    job = project.submit_job(job, timeout=120)
    if not args.skip_approval:
        for o in project.organizations:
            job.approve(org_id=o.id)

    print(f"\nSubmitted job {job} to run")

    return job


if __name__ == "__main__":
    if args.show_projects:
        list_projects()
        exit()

    if not args.skip_setup:
        setup_project()

    job = make_job()
    status = job.get_status()
    print("Waiting for job completion...")
    count = 0
    while status != "Completed" and status != "Error":
        if count > args.timeout:
            print(f"Timeout after {args.timeout} seconds")
            sys.exit(-1)

        status = job.get_status()
        time.sleep(1)
        count = count + 1

    print(f"Received status {status}. Exiting...")
    if status == "Completed":
        sys.exit()
    else:
        sys.exit(-1)
