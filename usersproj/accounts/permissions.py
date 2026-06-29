from .models import UserRole, Access, Resource


def check_permission(user, resource_name, action):
    if not user or not user.is_authenticated:
        return False

    try:
        resource = Resource.objects.get(name=resource_name)
    except Resource.DoesNotExist:
        return False

    user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
    if not user_roles:
        return False

    access_rules = Access.objects.filter(
        role_id__in=user_roles,
        resource=resource
    )
    for rule in access_rules:
        if action == 'read' and rule.can_read:
            # if obj and hasattr(obj, 'owner') and obj.owner != user:
                # continue
            return True

        elif action == 'read_all' and rule.can_read_all:
            return True

        elif action == 'create' and rule.can_create:
            return True

        elif action == 'update' and rule.can_update:
            # if obj and hasattr(obj, 'owner') and obj.owner != user:
                # continue
            return True

        elif action == 'update_all' and rule.can_update_all:
            return True

        elif action == 'delete' and rule.can_delete:
            # if obj and hasattr(obj, 'owner') and obj.owner != user:
                # continue
            return True

        elif action == 'delete_all' and rule.can_delete_all:
            return True

    return False