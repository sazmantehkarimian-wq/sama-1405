import os
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from domains.identity.models import UserProfile
from domains.properties.models import Center, CommercialSpace, MotherProperty, Region


@pytest.mark.django_db(transaction=True)
def test_real_chromium_uat_shell_auth_navigation_and_core_pages(live_server, tmp_path):
    from playwright.sync_api import Error, sync_playwright

    user = get_user_model().objects.create_user("browser-user", password="A-very-safe-password", is_staff=True)
    profile = UserProfile.objects.create(user=user, display_name="کاربر آزمون پذیرش", must_change_password=True)
    MotherProperty.objects.create(identifier="P-BROWSER",name="ملک آزمون مرورگر",source_row=2)
    region=Region.objects.create(code="2",name="منطقه ۲");regular=Center.objects.create(name="مرکز عادی",region=region);special_region=Region.objects.create(code="1",name="منطقه ۱");special=Center.objects.create(name="مرکز خاص",region=special_region,is_special=True)
    CommercialSpace.objects.create(code="10",name="فضای ده",status="ACTIVE",region=region,center=regular,source_row=10,source_classification="authority");CommercialSpace.objects.create(code="2",name="فضای دو",status="ACTIVE",region=region,center=regular,source_row=2,source_classification="authority");CommercialSpace.objects.create(code="1",name="فضای خاص",status="ACTIVE",region=special_region,center=special,source_row=1,source_classification="authority")
    CommercialSpace.objects.create(code="BROWSER-501", name="فضای آزمون مرورگر", status="ACTIVE", current_usage="فرهنگی", source_row=2, source_classification="authority")
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
        routes=[("dashboard","/"),("mother-properties","/mother-properties/"),("mother-dossier","/mother-properties/P-BROWSER/"),("contract-circulation","/contract-circulation/"),("active-spaces","/spaces/?status=ACTIVE"),("out-of-cycle","/spaces/?status=OUT_OF_CYCLE"),("dossier","/spaces/BROWSER-501/"),("contracts","/records/contracts/"),("beneficiaries","/records/beneficiaries/"),("appraisals","/records/appraisals/"),("fees","/records/fees/"),("auction","/auctions/"),("commission","/commissions/"),("utilities","/records/utilities/"),("workflows","/records/workflows/"),("documents","/records/documents/"),("alerts","/records/alerts/"),("reports","/reports/"),("users","/users/")]
        for width,height in ((1366,768),(1600,900),(1920,1080)):
            page.set_viewport_size({"width":width,"height":height})
            for name,path in routes:
                page.goto(f"{live_server.url}{path}");page.wait_for_load_state("networkidle");page.evaluate("scrollTo(0, 0)")
                assert page.locator("html").get_attribute("dir")=="rtl"
                assert page.locator('.topnav [aria-current="page"]').count()>=1
                assert page.locator(".account-name",has_text="کاربر آزمون پذیرش").is_visible()
                assert page.locator(".topnav",has_text="خروج").count()==0
                geometry = page.evaluate("""() => {
                  const nav = document.querySelector('.topnav');
                  const items = [...nav.children].map((item) => item.getBoundingClientRect());
                  const box = nav.getBoundingClientRect();
                  return {center: box.left + box.width / 2, viewportCenter: innerWidth / 2,
                    heights: items.map((item) => Math.round(item.height)),
                    centers: items.map((item) => Math.round(item.top + item.height / 2)),
                    fits: nav.scrollWidth <= nav.clientWidth};
                }""")
                assert abs(geometry["center"] - geometry["viewportCenter"]) <= 2
                assert page.evaluate("[...document.querySelectorAll('.brand-shell,.account')].every(el => { const r=el.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth })")
                assert len(set(geometry["heights"])) == 1 and len(set(geometry["centers"])) == 1 and geometry["fits"]
                if name == "active-spaces":
                    codes=page.locator("tbody tr td:first-child").all_inner_texts();assert codes[:2]==["2","10"] and codes.count("1")==1
                if name == "contract-circulation":
                    assert page.locator(".topnav details.active summary",has_text="قراردادها").get_attribute("aria-current")=="page"
                    assert page.locator("[data-search-picker]").count() >= 1 and page.locator("[data-search-picker]").first.is_visible() and page.locator('select[name="space_code"]').count()==0
                if name == "dossier":
                    tabs = page.locator(".tabs a")
                    tab_boxes = tabs.evaluate_all("els => els.map(el => { const r=el.getBoundingClientRect(); return [Math.round(r.top+r.height/2), Math.round(r.height)] })")
                    assert len({box[0] for box in tab_boxes}) == 1 and len({box[1] for box in tab_boxes}) == 1
                    assert page.locator('.tabs [aria-current="location"]').count() == 1
                    page.screenshot(path=evidence / f"dossier-top-{width}.png", full_page=False)
                    page.locator(".tabs").scroll_into_view_if_needed()
                    page.screenshot(path=evidence / f"dossier-tabs-{width}.png", full_page=False)
                assert not any(raw in page.locator("body").inner_text() for raw in ("PERSON","OPEN","MEDIUM","Legacy"))
                assert page.evaluate("scrollX === 0 && document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
                page.screenshot(path=evidence / f"{name}-{width}.png", full_page=True)
        page.goto(f"{live_server.url}/spaces/");page.get_by_label("جست‌وجوی سراسری").fill("BROWSER-501");page.get_by_role("button",name="جست‌وجو").click();page.get_by_role("link",name="مشاهده پرونده").click()
        assert "فضای BROWSER-501" in page.locator("h1").inner_text()
        for label,title in (("شروع گردش قرارداد","ایجاد پرونده گردش قرارداد"),("ثبت کارشناسی جدید","ثبت کارشناسی جدید"),("بارگذاری سند","بارگذاری سند"),("ثبت انشعاب / مصرف","ثبت انشعاب یا مصرف"),("ثبت تحویل","ثبت تحویل پرونده"),("ثبت مورد پیگیری","ثبت مورد نیازمند پیگیری")):
            page.get_by_role("link",name=label,exact=True).click()
            assert page.get_by_role("heading",name=title,exact=True).is_visible()
            assert "پرونده فضای BROWSER-501" in page.locator(".page-header").inner_text()
            if label == "شروع گردش قرارداد": page.screenshot(path=evidence / "contract-operation-context-1366.png", full_page=True)
            page.get_by_role("link",name="بازگشت به پرونده").click()
            assert "فضای BROWSER-501" in page.locator("h1").inner_text()
    finally:
        browser.close();manager.stop()


@pytest.mark.django_db(transaction=True)
def test_visual_freeze_regions_header_report_and_picker_in_browser(live_server):
    from playwright.sync_api import Error, sync_playwright
    user=get_user_model().objects.create_user('visual-browser',password='A-very-safe-password',is_staff=True)
    UserProfile.objects.create(user=user,display_name='کاربر بصری',must_change_password=False)
    region=Region.objects.create(code='6',name='منطقه ۶');center=Center.objects.create(name='مرکز شش',region=region);special=Center.objects.create(name='مرکز خاص شش',region=region,is_special=True)
    CommercialSpace.objects.create(code='61',name='فضای منطقه شش',status='ACTIVE',region=region,center=center,source_row=1,source_classification='authority')
    CommercialSpace.objects.create(code='62',name='فضای مرکز خاص',status='ACTIVE',region=region,center=special,source_row=2,source_classification='authority')
    manager=None
    try:
        manager=sync_playwright().start();browser=manager.chromium.launch(headless=True)
    except Error:
        if manager:manager.stop()
        if os.environ.get('SAMA_REQUIRE_BROWSER')=='1':raise
        pytest.skip('Chromium binary is not installed')
    try:
        page=browser.new_page(viewport={'width':1366,'height':768});page.goto(f'{live_server.url}/login/')
        page.get_by_label('نام کاربری').fill(user.username);page.get_by_label('گذرواژه').fill('A-very-safe-password');page.get_by_role('button',name='ورود').click()
        page.goto(f'{live_server.url}/regions/6/');page.wait_for_load_state('networkidle')
        assert page.get_by_text('منطقه ۶ — نمای مدیریتی',exact=True).is_visible()
        assert page.get_by_role('link',name='مراکز خاص').first.is_visible()
        assert page.get_by_text('مدیریت اقتصادی و املاک',exact=True).is_visible() and page.get_by_text('اداره املاک و مستغلات',exact=True).is_visible()
        page.goto(f'{live_server.url}/reports/?domain=mother_properties')
        assert page.get_by_role('link',name='املاک مادر',exact=True).count()>=1
        assert page.get_by_label('ردیف خالی خروجی').is_visible()
        page.goto(f'{live_server.url}/auctions/')
        picker=page.locator('[data-search-picker]').first;query=picker.locator('[data-picker-query]');query.fill('61');query.focus()
        picker.locator('[data-picker-option]').filter(has_text='61').first.click()
        assert 'open' not in (picker.get_attribute('class') or '')
    finally:
        browser.close();manager.stop()


@pytest.mark.django_db(transaction=True)
def test_fixed_uat_admin_owner_login_and_management_lock_in_browser(live_server, settings):
    settings.SAMA_UAT_FIXED_ADMIN=True;settings.SAMA_UAT_ADMIN_USERNAME="admin";settings.SAMA_UAT_ADMIN_PASSWORD="admin"
    from core.uat import provision_fixed_uat_admin
    from playwright.sync_api import Error, sync_playwright
    fixed=provision_fixed_uat_admin();manager=None
    try:
        manager=sync_playwright().start();browser=manager.chromium.launch(headless=True)
    except Error:
        if manager: manager.stop()
        if os.environ.get("SAMA_REQUIRE_BROWSER")=="1": raise
        pytest.skip("Chromium binary is not installed; explicit browser gate installs it")
    try:
        page=browser.new_page(viewport={"width":1366,"height":768})
        page.goto(f"{live_server.url}/login/");page.get_by_label("نام کاربری").fill("admin");page.get_by_label("گذرواژه").fill("admin");page.get_by_role("button",name="ورود").click()
        assert page.url.rstrip("/")==live_server.url
        page.locator(".account summary").click();assert page.get_by_role("link",name="تغییر گذرواژه").count()==0
        page.goto(f"{live_server.url}/users/");row=page.locator("tr",has_text="admin")
        assert row.get_by_text("مدیر ثابت UAT").is_visible()
        assert row.get_by_role("button",name="بازنشانی گذرواژه").count()==0
        assert row.get_by_role("button",name="غیرفعال‌سازی").count()==0
    finally:
        browser.close();manager.stop()
    fixed.refresh_from_db();assert fixed.username=="admin" and fixed.check_password("admin") and fixed.is_active and not fixed.profile.must_change_password
