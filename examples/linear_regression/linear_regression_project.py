from cape.api.dataview import DataView
from cape.api.job import VerticalLinearRegressionJob
from cape.cape import Cape

token='01EWK4XSCBNXV2V125R5VARZWJ,AWTFgsAy_cbZeO6ZvuYEuPv4BH4k0Q7eKA'
project_id='01EWK49HDBWKKXPZD2KHSP1EVW'


def list_projects():
    c = Cape(endpoint='http://localhost:8080')
    c.login(token=token)
    print('projects')
    for p in c.list_projects():
        print(f'\t{p}')


def get_project():
    c = Cape(endpoint='http://localhost:8080')
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
    c = Cape(endpoint='http://localhost:8080')
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
        'cpp': 'https://storage.googleapis.com/worker-data/x_data.csv',
        'cts': 'https://storage.googleapis.com/worker-data/y_data.csv',
    }

    for org in project.organizations:
        # print('orgID', org.id)
        dv = DataView(name=f"{org.name}-data", owner_id=org.id, uri=org_dv[org.name])
        print(project.add_dataview(dv))


def make_job():
    c = Cape(endpoint='http://localhost:8080')
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
    )

    job = project.create_job(job=job)
    print('\nCreated Job')
    print(f'\t{job}')

    print(f'\nSubmitted job {job.submit_job()} to run')


if __name__ == '__main__':
    # list_projects()
    # get_project()
    setup_project()
    make_job()
