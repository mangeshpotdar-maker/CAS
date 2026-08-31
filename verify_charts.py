from playwright.sync_api import sync_playwright

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 1600},
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            page.goto("http://localhost:8501")
            page.wait_for_timeout(3000)

            # Click RUN 3:22 ANALYSIS
            run_btn = page.get_by_role("button", name="RUN 3:22 ANALYSIS")
            if run_btn.is_visible():
                run_btn.click()
                page.wait_for_timeout(3000)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            page.screenshot(path="/home/jules/verification/screenshots/side_by_side_charts.png", full_page=True)
            page.wait_for_timeout(1000)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_verification()
