import argparse
import os

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

def list_projects():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    print('projects')
    for p in c.list_projects():
        print(f'\t{p}')


def get_project():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    project = c.get_project(id=project_id)
    print(project)
    print('\nOrgs:')
    for o in project.organizations:
        print(f'\t{o}')

    print('\nData Views:')
    for dv in project.dataviews:
        print(f'\t{dv}')


def setup_project():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    print('projects')
    for p in c.list_projects():
        print(f'\t{p}')

    print()

    project = c.get_project(id=project_id)
    print('linear-regression-project')
    print(f'\t{project}')
    print('orgs', project.organizations)

    org_dv = {
        project.organizations[0].name: 'https://storage.googleapis.com/worker-data/x_data.csv',
        project.organizations[1].name: 'https://storage.googleapis.com/worker-data/y_data.csv',
    }

    for org in project.organizations:
        try:
            dv = DataView(name=f"{org.name}-data", owner_id=org.id, uri=org_dv[org.name])
        except KeyError:
            continue
        print(project.add_dataview(dv))


def make_job():
    c = Cape(endpoint=coordinator_url)
    c.login(token=token)
    project = c.get_project(id=project_id)
    print(project)
    print('\nOrgs:')
    for o in project.organizations:
        print(f'\t{o}')

    print('\nData Views:')
    for dv in project.dataviews:
        print(f'\t{dv}')

    job = VerticalLinearRegressionJob(
        x_train_dataview=project.dataviews[0],
        x_train_data_cols=['col1'],
        y_train_dataview=project.dataviews[1],
        y_train_data_cols=['col1'],
        # the cape org
        third_party_org_id=project.organizations[2].id,
    )

    job = project.create_job(job=job)
    print('\nCreated Job')
    print(f'\t{job}')

    print(f'\nSubmitted job {job.submit_job()} to run')


if __name__ == '__main__':
    if args.show_projects:
        list_projects()
        exit()

    if not args.skip_setup:
        setup_project()

    make_job()
