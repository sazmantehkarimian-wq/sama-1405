"""Single policy boundary for the explicitly enabled Owner UAT credential."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from domains.identity.models import UserProfile


def is_fixed_uat_admin(user) -> bool:
    return bool(
        settings.SAMA_UAT_FIXED_ADMIN and user.is_authenticated
        and user.username == settings.SAMA_UAT_ADMIN_USERNAME
    )


@transaction.atomic
def provision_fixed_uat_admin():
    """Idempotently restore the UAT-only admin contract on every startup."""
    if not settings.SAMA_UAT_FIXED_ADMIN:
        return None
    user, _ = get_user_model().objects.get_or_create(
        username=settings.SAMA_UAT_ADMIN_USERNAME,
        defaults={"first_name": "مدیر", "last_name": "سما"},
    )
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password(settings.SAMA_UAT_ADMIN_PASSWORD)
    user.save(update_fields=["password", "is_active", "is_staff", "is_superuser"])
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"display_name": "مدیر سما"})
    profile.display_name = profile.display_name or "مدیر سما"
    profile.must_change_password = False
    profile.operational_access = True
    profile.save(update_fields=["display_name", "must_change_password", "operational_access"])
    return user
