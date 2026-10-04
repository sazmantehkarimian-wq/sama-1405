from core.uat import is_fixed_uat_admin


def uat_policy(request):
    from django.conf import settings
    user=getattr(request,'user',None)
    fixed=bool(user and getattr(user,'is_authenticated',False) and is_fixed_uat_admin(user))
    return {"is_fixed_uat_admin":fixed,"uat_fixed_admin_enabled":settings.SAMA_UAT_FIXED_ADMIN,"uat_admin_username":settings.SAMA_UAT_ADMIN_USERNAME}
