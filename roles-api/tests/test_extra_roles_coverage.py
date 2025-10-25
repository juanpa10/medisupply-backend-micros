import pytest

# Delay importing application modules until tests run so conftest can set sys.path / env


class RepoReturnsTuple:
    def access_control(self, email, rol, action):
        return ({"error": "user_not_exist"}, 200)


class RepoReturnsDict:
    def access_control(self, email, rol, action):
        return {"error": "user_not_exist"}


class GoodClass:
    def __init__(self):
        self.email = "a@x"
        self.rol = "R"
        self.action = "view"
        self.permission = True


class BadInitClass:
    def __init__(self):
        raise RuntimeError("boom")


class RepoReturnsTypeGood:
    def access_control(self, email, rol, action):
        return GoodClass


class RepoReturnsTypeBad:
    def access_control(self, email, rol, action):
        return BadInitClass


def test_access_control_normalizes_tuple_and_dict():
    # import inside test to ensure test harness has configured sys.path
    from app.services.roles_service import RolesService
    svc1 = RolesService(repo=RepoReturnsTuple())
    o1 = svc1.access_control("x@x", "Whatever", "view")
    assert hasattr(o1, "permission")
    assert o1.permission is False

    svc2 = RolesService(repo=RepoReturnsDict())
    o2 = svc2.access_control("x@x", "Whatever", "view")
    assert hasattr(o2, "permission")
    assert o2.permission is False


def test_access_control_instantiates_type_or_fallsback():
    from app.services.roles_service import RolesService
    svc_good = RolesService(repo=RepoReturnsTypeGood())
    got = svc_good.access_control("a@b", "R", "view")
    # GoodClass should be instantiated and permission True
    assert getattr(got, "permission", None) is True

    svc_bad = RolesService(repo=RepoReturnsTypeBad())
    got2 = svc_bad.access_control("a@b", "R", "view")
    # Instantiation failed; fallback should produce permission False
    assert getattr(got2, "permission", None) is False


def test_set_user_roles_with_real_repo(app):
    # ensure app fixture has initialized the DB and env
    from app.repositories.repo import Repo
    from app.services.roles_service import RolesService

    repo = Repo()

    # create a unique role and user to avoid collisions with other tests
    role = repo.create_role("TestrRoleX", "desc")
    user = repo.create_user("Test User X", f"testuserx_{role.id}@example.com", "pwd")

    svc = RolesService(repo=repo)
    mapped = svc.set_user_roles(user.id, [{"role_id": role.id, "can_view": True}])
    assert isinstance(mapped, dict)
    assert mapped["id"] == user.id
    assert len(mapped["roles"]) == 1
    assert mapped["roles"][0]["name"] == role.name
