from cape.api.dataview import DataView
from cape.api.job import MultiplicationJob
from cape.cape import Cape
from cape.api.project import Project


token='01EWJK9ZNVMK40XQXGHEZ7GKPJ,ASWK9li3QQNCUEO0a6WED0woLwjCQ1J0ww'

cape_org_id='01EWJKAF60ET7FNSQ8MNNV1A21'
cts_org_id='01EWJKATMPV156JCACAKN6NCQ6'
cape_proj_label='cape_mult'

def create_or_get_project(name, org_id):
    c = Cape(endpoint='http://localhost:8080')
    c.login(token=token)
    print('create project', name)
    try:
        return c.create_project(name=name, owner=org_id, description="org desc")
    except:
        return c.get_project(label=name)


def add_project_to_org(project, org_id):
    c = Cape(endpoint='http://localhost:8080')
    c.login(token=token)
    print('add org to project')
    project.add_org(org_id=org_id)

def list_projects():
    c = Cape(endpoint='http://localhost:8080')
    c.login(token=token)
    print('projects')
    for p in c.list_projects():
        print(f'\t{p}')


def get_project(id = None, label = None):
    c = Cape(endpoint='http://localhost:8080')
    c.login(token=token)
    return c.get_project(id=id, label=label)


def setup_project(project_id):
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
        'cape': 'https://storage.googleapis.com/worker-data/x_data.csv',
        'cts': 'https://storage.googleapis.com/worker-data/y_data.csv',
    }

    for org in project.organizations:
        dv = DataView(name=f"{org.name}-data", owner_id=org.id, uri=org_dv[org.name])
        print(project.create_dataview(dv))


def make_job(project_id):
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

    job = MultiplicationJob()

    mult_job = project.create_job(job=job)
    print('\nCreated Job')
    print(f'\t{mult_job}')

    mult_job.assign_job_roles(inputter0=cape_org_id, inputter1=cts_org_id)

    j = mult_job.submit_job()
    print(f'\nSubmitted job {j} to run')
    return j


if __name__ == '__main__':
    list_projects()
    
    cape = create_or_get_project(cape_proj_label, cape_org_id)

    add_project_to_org(cape, cts_org_id)

    # setup_project(cape.id)

    make_job(cape.id)
