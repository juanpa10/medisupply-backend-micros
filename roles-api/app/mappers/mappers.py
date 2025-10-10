from app.domain.models import User

def map_user_with_roles(user: User) -> dict:
    return {
        "id": user.id,
        "names": user.names,
        "email": user.email,
        "roles": [
            {
                "id": a.role.id,
                "name": a.role.name,
                "description": a.role.description,
                "can_create": bool(a.can_create),
                "can_edit": bool(a.can_edit),
                "can_delete": bool(a.can_delete),
                "can_view": bool(a.can_view),
            }
            for a in user.roles_assocs
        ],
    }
