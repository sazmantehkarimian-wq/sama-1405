#!/usr/bin/env python3
"""Apply owner-approved UAT branding and remove legacy release artefacts."""
from __future__ import annotations

import argparse
import colorsys
import gzip
import re
import shutil
import zipfile
from pathlib import Path


VERSION = "4.0.0-uat.3"
LOGO_ARCHIVE = "لوگو جدید سازمان.zip"
LEGACY_ROOT_GLOBS = ("VERSION_v3*", "RELEASE_NOTES_v3*", "MANIFEST_SHA256_v3*")
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")


def approved_logo(repository: Path) -> bytes:
    with zipfile.ZipFile(repository / LOGO_ARCHIVE) as archive:
        names = [name for name in archive.namelist() if name.endswith("آرم جدید سازمان.png.jpeg")]
        if len(names) != 1:
            raise RuntimeError("The approved purple organization logo was not found exactly once")
        return archive.read(names[0])


def replacement_color(match: re.Match[str]) -> str:
    """Remove blue/cyan and muddy-green colors without touching neutral or purple colors."""
    value = match.group(0)
    red, green, blue = (int(value[index:index + 2], 16) / 255 for index in (1, 3, 5))
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    degrees = hue * 360
    if saturation >= 0.18 and 165 <= degrees <= 255:
        if lightness < 0.28:
            return "#684c6d"
        if lightness < 0.52:
            return "#89688d"
        if lightness < 0.78:
            return "#bda9bf"
        return "#f2edf3"
    if saturation >= 0.22 and 55 <= degrees <= 145 and lightness < 0.52:
        return "#39735f"
    return value.lower()


def rewrite_design_system(internal: Path) -> None:
    core_locations = (
        internal / "staticfiles/css/organizational_core_v340.css",
        internal / "amlak/static/css/organizational_core_v340.css",
    )
    semantic_tokens = """
/* SAMA UAT 4.0.0-uat.3 — owner-approved light organizational palette. */
:root{
  --brand-primary:#765579;
  --brand-primary-hover:#634766;
  --brand-primary-soft:#eee7ef;
  --brand-accent:#a67b5b;
  --brand-success:#39735f;
  --brand-canvas:#f7f4f6;
  --brand-surface:#ffffff;
  --brand-text:#352f36;
  --brand-muted:#6f6871;
  --navy-950:#765579;--navy-900:#765579;--navy-850:#806184;
  --navy-800:#89688d;--navy-700:#98799b;
  --teal-700:#765579;--teal-600:#89688d;--teal-500:#a386a6;
  --teal-100:#eee7ef;--teal-50:#f8f5f8;
  --ink-950:#2f2930;--ink-900:#352f36;--ink-800:#49424a;
  --ink-700:#5b545d;--ink-600:#6f6871;--ink-500:#817a83;
  --canvas:var(--brand-canvas);--surface:var(--brand-surface);
  --shadow-sm:0 1px 2px rgba(53,47,54,.04),0 6px 20px rgba(53,47,54,.06);
  --shadow-md:0 14px 36px rgba(53,47,54,.12);
}
"""
    for path in internal.rglob("*"):
        if path.suffix.lower() not in {".css", ".html"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = HEX_COLOR.sub(replacement_color, text)
        text = text.replace("Identity: navy, turquoise, white and controlled orange accents.",
                            "Identity: light plum, warm neutral, white and controlled copper accents.")
        if path in core_locations:
            text += semantic_tokens
        if path.name == "organizational_pages_v340.css":
            text += """
/* Login consumes the central semantic tokens; no page-local dark/navy palette. */
.login-page{background:var(--brand-canvas)}
.login-shell{border:1px solid #e2d9e3;box-shadow:0 22px 60px rgba(53,47,54,.14)}
.login-brand-panel{background:linear-gradient(145deg,#89688d,#a386a6);color:#fff}
.login-brand-panel::after{border-color:rgba(255,255,255,.18);box-shadow:0 0 0 46px rgba(255,255,255,.05),0 0 0 92px rgba(255,255,255,.025)}
.login-form-panel{background:var(--brand-surface)}
.login-kicker,.login-credit b{color:#f4e6d9}
.login-submit{background:var(--brand-primary)!important;border-color:var(--brand-primary)!important}
"""
        path.write_text(text, encoding="utf-8")
        compressed = path.with_name(path.name + ".gz")
        if compressed.exists():
            compressed.write_bytes(gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0))


def prepare(repository: Path, package: Path) -> None:
    for pattern in LEGACY_ROOT_GLOBS:
        for path in package.glob(pattern):
            path.unlink()
    qa = package / "QA"
    if qa.exists():
        shutil.rmtree(qa)
    qa.mkdir()
    logs = package / "logs"
    if logs.exists():
        for path in logs.iterdir():
            if path.is_file():
                path.unlink()
    obsolete_check = package / "CHECK_RUNNING_VERSION.bat"
    if obsolete_check.exists():
        obsolete_check.unlink()

    internal = package / "app/_internal"
    rewrite_design_system(internal)
    logo = approved_logo(repository)
    for root in (internal / "staticfiles", internal / "amlak/static"):
        image_dir = root / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        (image_dir / "org_logo.jpeg").write_bytes(logo)
    for template in (internal / "amlak/templates").rglob("*.html"):
        text = template.read_text(encoding="utf-8").replace("images/org_logo.png", "images/org_logo.jpeg")
        text = text.replace("#062b52", "#765579").replace("نسخه سازمانی ۳.۴.۰", "نسخه سازمانی ۴.۰.۰ UAT 3")
        template.write_text(text, encoding="utf-8")

    (package / "CURRENT_VERSION.txt").write_text(
        f"SAMA Enterprise LAN\nVersion: {VERSION}\nRelease channel: UAT\nPort: 8765\n",
        encoding="utf-8",
    )
    readme = """سامانه جامع مدیریت املاک — نسخه ۴.۰.۰ UAT 3
سازمان فرهنگی هنری شهرداری تهران
مدیریت اقتصادی و املاک — اداره املاک و مستغلات

۱. بسته را در یک پوشه جدید Extract کنید.
۲. START_SERVER.bat را اجرا کنید.
۳. روی سرور به http://127.0.0.1:8765 و در شبکه به http://SERVER-IP:8765 بروید.
۴. برای پشتیبان‌گیری و بازیابی از فایل‌های BACKUP_NOW.bat و RESTORE_BACKUP.bat استفاده کنید.

گزارش Import و کنترل‌های این نسخه در پوشه QA قرار دارد.
"""
    (package / "README_FA.txt").write_text(readme, encoding="utf-8")
    (package / "شروع_از_اینجا.txt").write_text(readme, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.repository.resolve(), args.package.resolve())


if __name__ == "__main__":
    main()
