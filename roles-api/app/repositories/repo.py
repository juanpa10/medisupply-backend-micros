from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.domain.models import User, Role, UserRole

class Repo:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    def list_users(self): return self.session.execute(select(User)).scalars().all()
    def get_user(self, uid:int): return self.session.get(User, uid)
    def create_user(self, names:str, email:str, password:str|None=None):
        # check for existing email first to avoid unique constraint exceptions
        existing = self.session.execute(select(User).filter_by(email=email)).scalars().first()
        if existing:
            raise ValueError("email_exists")

        try:
            u = User(names=names, email=email, password=password)
            self.session.add(u)
            self.session.commit()
            self.session.refresh(u)
            return u
        except IntegrityError:
            # ensure session is clean for next transaction
            try:
                self.session.rollback()
            except Exception:
                pass
            # re-raise as a generic error for controller to handle
            raise

    def list_roles(self): return self.session.execute(select(Role)).scalars().all()
    def create_role(self, name:str, description:str|None=None):
        r = Role(name=name, description=description); self.session.add(r); self.session.commit(); self.session.refresh(r); return r
    def get_role(self, rid:int): return self.session.get(Role, rid)
    def get_role_by_name(self, name: str):
        return self.session.execute(select(Role).filter_by(name=name)).scalars().first()

    def set_user_roles(self, uid:int, items:list[dict]):
        u = self.get_user(uid)
        if not u: return None
        self.session.execute(delete(UserRole).where(UserRole.user_id==uid))
        self.session.commit()
        for it in items:
            r = self.get_role(it["role_id"])
            if not r: 
                continue
            assoc = UserRole(
                user_id=uid, role_id=r.id,
                can_create=bool(it.get("can_create", False)),
                can_edit=bool(it.get("can_edit", False)),
                can_delete=bool(it.get("can_delete", False)),
                can_view=bool(it.get("can_view", True)),
            )
            self.session.add(assoc)
        self.session.commit(); self.session.refresh(u); return u
    
    def access_control(self, email, rol, action):
        u = self.session.execute(select(User).filter_by(email=email)).scalars().first()
        if not u:
            return {"error": "user_not_exist"}, 200
        
        role = self.session.execute(select(Role).filter_by(name=rol)).scalars().first()
        if not role:
            raise ValueError("role_not_found")
        
        user_role = self.session.execute(
            select(UserRole).filter_by(user_id=u.id, role_id=role.id)
        ).scalars().first()
        
        if not user_role:
            return type('Obj', (object,), {'email': email, 'rol': rol, 'action': action, 'permission': False})
        
        permission = False
        if action == "create":
            permission = user_role.can_create
        elif action == "edit":
            permission = user_role.can_edit
        elif action == "delete":
            permission = user_role.can_delete
        elif action == "view":
            permission = user_role.can_view
        else:
            raise ValueError("invalid_action")
        
        return type('Obj', (object,), {'email': email, 'rol': rol, 'action': action, 'permission': permission})
