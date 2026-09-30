import os
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from domains.properties.models import CommercialSpace


@pytest.mark.django_db(transaction=True)
def test_real_chromium_rtl_navigation_filter_and_dossier(live_server, tmp_path):
    from playwright.sync_api import Error, sync_playwright

    user = get_user_model().objects.create_user("browser-user", password="A-very-safe-password")
    CommercialSpace.objects.create(
        code="BROWSER-501", name="فضای آزمون مرورگر", status="ACTIVE",
        current_usage="فرهنگی", source_row=2, source_classification="authority",
    )
    try:
        manager = sync_playwright().start()
        browser = manager.chromium.launch(headless=True)
    except Error:
        if os.environ.get("SAMA_REQUIRE_BROWSER") == "1":
            raise
        pytest.skip("Chromium binary is not installed; CI browser gate installs it explicitly")
    try:
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(f"{live_server.url}/login/")
        page.get_by_label("نام کاربری").fill(user.username)
        page.get_by_label("گذرواژه").fill("A-very-safe-password")
        page.get_by_role("button", name="ورود").click()
        page.goto(f"{live_server.url}/spaces/")
        assert page.locator("html").get_attribute("dir") == "rtl"
        assert page.locator(".app-sidebar").count() == 0
        page.get_by_label("جست‌وجوی سراسری").fill("BROWSER-501")
        page.get_by_role("button", name="جست‌وجو").click()
        page.get_by_role("link", name="مشاهده پرونده").click()
        assert "پرونده فضای BROWSER-501" in page.locator("h1").inner_text()
        destination = os.environ.get("SAMA_BROWSER_SCREENSHOT")
        if destination:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=destination, full_page=True)
    finally:
        browser.close()
        manager.stop()
