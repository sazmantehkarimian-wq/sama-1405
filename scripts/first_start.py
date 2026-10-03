"""Fast, idempotent Zero-Data UAT startup preparation."""
from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sama.settings")

import django

django.setup()

from django.core.management import call_command

from core.uat import provision_fixed_uat_admin
from services.startup import StartupSafetyError, run_preflight


def main() -> None:
    print("[1/3] Startup safety check...")
    try:
        preflight = run_preflight()
    except (StartupSafetyError, ValueError, OSError) as exc:
        raise SystemExit(f"SAMA startup safety check failed: {exc}") from exc

    if preflight["backup"]:
        print(f"Startup safety backup: {preflight['backup']}")

    if preflight["pending"]:
        print(f"[2/3] Applying {len(preflight['pending'])} pending migration(s)...")
        call_command("migrate", interactive=False, verbosity=0)
    else:
        print("[2/3] Database schema is current; no migrations needed.")

    print("[3/3] Preparing UAT administrator...")
    provision_fixed_uat_admin()
    print("Startup preparation complete. Zero operational data preserved.")


if __name__ == "__main__":
    main()
