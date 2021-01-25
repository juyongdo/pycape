from cape.api.organization.organization import Organization


class TestOrganization:
    def test__repr__(self):
        id = "abc123"
        name = "fun-company"

        org = Organization(id=id, name=name)
        assert repr(org) == f"<{org.__class__.__name__} (id={id}, name={name})>"
