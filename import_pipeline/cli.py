"""Command line entry point for authority verification, inventory, and import."""
import argparse
import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sama.settings")

import django

django.setup()

from import_pipeline.authority_inventory import inspect_package, verify_manifest
from import_pipeline.import_authorities import run


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m import_pipeline.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("verify", "verify every SHA-256 entry in an authority directory"),
        ("inspect", "inspect the workbooks and validate canonical identities"),
        ("import", "run the lossless and canonical database import"),
    ):
        item = commands.add_parser(command, help=help_text)
        item.add_argument("path", type=Path)
    args = parser.parse_args()
    path = args.path.resolve()
    if args.command == "verify":
        result = verify_manifest(path)
    elif args.command == "inspect":
        result = inspect_package(path).as_dict()
    else:
        result = run(path)
    print(result)


if __name__ == "__main__":
    main()
