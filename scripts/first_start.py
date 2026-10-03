"""Idempotent local first-start setup; never emits passwords into CI/build logs."""
from __future__ import annotations

import os
import secrets
import string
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sama.settings")

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction

from core.uat import provision_fixed_uat_admin
from domains.identity.models import UserProfile
from services.startup import StartupSafetyError, run_preflight

USERS = (
    ("aghorbani", "اکبر", "قربانی", False),
    ("amajidi", "اکبر", "مجیدی", False),
    ("mabdollahi", "مجید", "عبدالهی", False),
    ("zmohammadi", "زهره", "محمدی", False),
    ("mkarimian", "سید محمد", "کریمیان", False),
    ("admin", "مدیر", "سامانه", True),
)


def password() -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(20))


def main() -> None:
    try:
        preflight = run_preflight()
    except (StartupSafetyError, ValueError, OSError) as exc:
        raise SystemExit(f"SAMA startup safety check failed: {exc}") from exc

    if preflight["backup"]:
        print(f"Startup safety backup: {preflight['backup']}")
    if preflight["pending"]:
        print(f"Applying {len(preflight['pending'])} pending migration(s) after verified backup.")

    call_command("migrate", interactive=False, verbosity=0)
    provision_fixed_uat_admin()
    credentials = []
    user_model = get_user_model()
    with transaction.atomic():
        for username, first, last, administrator in USERS:
            if settings.SAMA_UAT_FIXED_ADMIN and username == settings.SAMA_UAT_ADMIN_USERNAME:
                continue
            if user_model.objects.filter(username=username).exists():
                continue
            temporary = password()
            user = user_model.objects.create_user(
                username=username, password=temporary, first_name=first, last_name=last,
                is_staff=administrator, is_superuser=administrator,
            )
            UserProfile.objects.create(
                user=user, display_name=f"{first} {last}", must_change_password=True,
                operational_access=True,
            )
            credentials.append(f"{username}: {temporary}")
    if credentials:
        destination = Path(settings.BASE_DIR) / "FIRST_LOGIN_CREDENTIALS.txt"
        destination.write_text(
            "گذرواژه‌های موقت سما — پس از تحویل امن این فایل را حذف کنید.\n"
            "در نخستین ورود تغییر گذرواژه اجباری است.\n\n" + "\n".join(credentials) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
