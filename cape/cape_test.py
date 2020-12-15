from cape.cape import Cape


def test_list_projects():
    c = Cape()
    projects = c.list_projects()

    assert len(projects) == 0
