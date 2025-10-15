from app.repositories.repo import Repo
from app.mappers.mappers import map_user_with_roles

class RolesService:
    def __init__(self, repo: Repo|None=None):
        self.repo = repo or Repo()

    def seed(self):
        if not self.repo.list_roles():
            for n,d in [("Compras","Módulo Compras"),("Ventas","Módulo Ventas"),
                        ("Clientes","Módulo Clientes"),("Logística","Módulo Logística"),
                        ("Admin","Administrador")]:
                self.repo.create_role(n,d)
        if not self.repo.list_users():
            u1 = self.repo.create_user("Juan Pérez","juan@example.com","Ju4nP3r3z!")
            u2 = self.repo.create_user("María López","maria@example.com","M4r14L0p3z!")
            # assign Admin role to the first seeded user
            admin_role = self.repo.get_role_by_name("Admin")
            if admin_role and u1:
                self.repo.set_user_roles(u1.id, [{"role_id": admin_role.id, "can_create": True, "can_edit": True, "can_delete": True, "can_view": True}])

    def list_users_with_roles(self):
        return [map_user_with_roles(u) for u in self.repo.list_users()]

    def set_user_roles(self, uid:int, assignments:list[dict]):
        u = self.repo.set_user_roles(uid, assignments)
        return map_user_with_roles(u) if u else None

    def list_users(self): return self.repo.list_users()
    def list_roles(self): return self.repo.list_roles()
    def create_user(self, names,email,password=None, role_name: str|None=None):
        u = self.repo.create_user(names,email,password)
        if role_name and u:
            r = self.repo.get_role_by_name(role_name)
            if r:
                self.repo.set_user_roles(u.id, [{"role_id": r.id, "can_create": True, "can_edit": True, "can_delete": True, "can_view": True}])
        return u
    def create_role(self, name,desc=None): return self.repo.create_role(name,desc)
