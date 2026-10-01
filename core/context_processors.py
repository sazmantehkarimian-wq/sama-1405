from core.uat import is_fixed_uat_admin


def uat_policy(request):
    from django.conf import settings
    return {"is_fixed_uat_admin": is_fixed_uat_admin(request.user), "uat_fixed_admin_enabled": settings.SAMA_UAT_FIXED_ADMIN, "uat_admin_username": settings.SAMA_UAT_ADMIN_USERNAME}
