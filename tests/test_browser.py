import os
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from domains.identity.models import UserProfile
from domains.properties.models import CommercialSpace


@pytest.mark.django_db(transaction=True)
def test_real_chromium_uat_shell_auth_navigation_and_core_pages(live_server, tmp_path):
    from playwright.sync_api import Error, sync_playwright

    user = get_user_model().objects.create_user("browser-user", password="A-very-safe-password", is_staff=True)
    profile = UserProfile.objects.create(user=user, display_name="کاربر آزمون پذیرش", must_change_password=True)
    CommercialSpace.objects.create(code="9501", name="فضای آزمون مرورگر", status="ACTIVE", current_usage="فرهنگی")
    manager = None
    try:
        manager = sync_playwright().start();browser = manager.chromium.launch(headless=True)
    except Error:
        if manager: manager.stop()
        if os.environ.get("SAMA_REQUIRE_BROWSER") == "1": raise
        pytest.skip("Chromium binary is not installed; CI browser gate installs it explicitly")
    evidence = Path(os.environ.get("SAMA_BROWSER_SCREENSHOT_DIR", tmp_path / "browser"));evidence.mkdir(parents=True, exist_ok=True)
    try:
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.goto(f"{live_server.url}/login/")
        assert page.get_by_role("heading", name="سما", exact=True).is_visible()
        page.screenshot(path=evidence / "login-1366.png", full_page=True)
        page.get_by_label("نام کاربری").fill(user.username);page.get_by_label("گذرواژه").fill("A-very-safe-password");page.get_by_role("button", name="ورود").click()
        assert page.url.endswith("/account/password/")
        assert page.get_by_label("گذرواژه فعلی").is_visible() and page.get_by_label("تکرار گذرواژه جدید").is_visible()
        page.screenshot(path=evidence / "password-change-1366.png", full_page=True)
        page.get_by_label("گذرواژه فعلی").fill("A-very-safe-password");page.get_by_label("گذرواژه جدید", exact=True).fill("A-different-very-safe-password");page.get_by_label("تکرار گذرواژه جدید").fill("A-different-very-safe-password");page.get_by_role("button",name="ذخیره گذرواژه").click()
        assert page.url.rstrip("/")==live_server.url
        routes=[("dashboard","/"),("active-spaces","/spaces/?status=ACTIVE"),("out-of-cycle","/spaces/?status=OUT_OF_CYCLE"),("dossier","/spaces/9501/"),("contracts","/records/contracts/"),("beneficiaries","/records/beneficiaries/"),("appraisals","/records/appraisals/"),("fees","/records/fees/"),("auction","/auctions/"),("commission","/commissions/"),("utilities","/records/utilities/"),("workflows","/records/workflows/"),("documents","/records/documents/"),("alerts","/records/alerts/"),("reports","/reports/"),("users","/users/")]
        for width,height in ((1366,768),(1920,1080)):
            page.set_viewport_size({"width":width,"height":height})
            for name,path in routes:
                page.goto(f"{live_server.url}{path}");page.wait_for_load_state("networkidle")
                assert page.locator("html").get_attribute("dir")=="rtl"
                assert page.locator('.topnav [aria-current="page"]').count()>=1
                assert page.locator(".account-name",has_text="کاربر آزمون پذیرش").is_visible()
                assert page.locator(".topnav",has_text="خروج").count()==0
                assert not any(raw in page.locator("body").inner_text() for raw in ("PERSON","OPEN","MEDIUM","Legacy"))
                assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
                page.screenshot(path=evidence / f"{name}-{width}.png", full_page=True)
        page.goto(f"{live_server.url}/spaces/");page.get_by_label("جست‌وجوی سراسری").fill("9501");page.get_by_role("button",name="جست‌وجو").click();page.get_by_role("link",name="مشاهده پرونده").click()
        assert "پرونده فضای 9501" in page.locator("h1").inner_text()
    finally:
        browser.close();manager.stop()
