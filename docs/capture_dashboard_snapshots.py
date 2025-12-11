"""
Capture Dashboard Snapshots
============================
Automatically takes screenshots of each tab/view in the DC-Intel dashboard
for documentation and sharing purposes.

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import os
from datetime import datetime

from playwright.async_api import async_playwright

# Configuration
DASHBOARD_URL = "http://localhost:8080/site/dashboard_v2.html"
OUTPUT_DIR = r"C:\Users\Yaseen\dc-intel\site\snapshots"
VIEWPORT_SIZE = {"width": 1920, "height": 1080}  # Full HD

# Pages to capture with navigation/tab context
PAGES = [
    {
        "name": "00_home_full_page",
        "title": "Home - Full Page",
        "section": "home",
        "scroll_to": None,
        "wait_for": "body",
        "delay": 2000,
        "full_page": True,
    },
    {
        "name": "01_header_hero",
        "title": "Home - Header & Hero",
        "section": "home",
        "scroll_to": "h1",
        "wait_for": "h1",
        "delay": 1500,
    },
    {
        "name": "02_news_section",
        "title": "Home - Latest News",
        "section": "home",
        "scroll_to": "text=Latest Data Center News",
        "wait_for": "text=Latest Data Center News",
        "delay": 1500,
    },
    {
        "name": "03_knowledge_base",
        "title": "Knowledge Base - Glossary",
        "section": "knowledge",
        "scroll_to": "#knowledgeSection",
        "wait_for": "#knowledgeSection",
        "delay": 1500,
    },
    {
        "name": "03b_knowledge_handbook",
        "title": "Knowledge Base - Handbook",
        "section": "knowledge",
        "knowledge_tab": "handbook",
        "scroll_to": "#knowledgeSection",
        "wait_for": "#handbookView",
        "delay": 2000,
    },
    {
        "name": "03c_knowledge_taxonomy",
        "title": "Knowledge Base - Taxonomy",
        "section": "knowledge",
        "knowledge_tab": "taxonomy",
        "scroll_to": "#knowledgeSection",
        "wait_for": "#taxonomyView",
        "delay": 2000,
    },
    {
        "name": "03d_knowledge_studyguides",
        "title": "Knowledge Base - Study Guides",
        "section": "knowledge",
        "knowledge_tab": "studyguides",
        "scroll_to": "#knowledgeSection",
        "wait_for": "#studyguidesView",
        "delay": 2000,
    },
    {
        "name": "04_subscription_pricing",
        "title": "Subscription Pricing",
        "section": "pricing",
        "scroll_to": "#pricingSection",
        "wait_for": "#pricingSection",
        "delay": 1500,
    },
    {
        "name": "05_advisory_services",
        "title": "Advisory & Intelligence Services",
        "section": "services",
        "scroll_to": "#servicesSection",
        "wait_for": "#servicesSection",
        "delay": 1500,
    },
    {
        "name": "06_existing_heatmap",
        "title": "Existing DCs - Heatmap",
        "section": "existing-dcs",
        "existing_tab": "heatmap",
        "scroll_to": "#existingTabHeatmapContent",
        "wait_for": "#existingTabHeatmapContent",
        "delay": 2500,
    },
    {
        "name": "07_existing_table",
        "title": "Existing DCs - Table",
        "section": "existing-dcs",
        "existing_tab": "table",
        "scroll_to": "#existingTabTableContent",
        "wait_for": "#existingTabTableContent",
        "delay": 2500,
    },
    {
        "name": "08_existing_contact",
        "title": "Existing DCs - Request Data",
        "section": "existing-dcs",
        "existing_tab": "contact",
        "scroll_to": "#existingTabContactContent",
        "wait_for": "#existingTabContactContent",
        "delay": 1500,
    },
    {
        "name": "09_upcoming_heatmap",
        "title": "Upcoming DCs - Heatmap",
        "section": "upcoming-dcs",
        "upcoming_tab": "heatmap",
        "scroll_to": "#upcomingTabHeatmapContent",
        "wait_for": "#upcomingTabHeatmapContent",
        "delay": 2500,
    },
    {
        "name": "10_upcoming_table",
        "title": "Upcoming DCs - Table",
        "section": "upcoming-dcs",
        "upcoming_tab": "table",
        "scroll_to": "#upcomingTabTableContent",
        "wait_for": "#upcomingTabTableContent",
        "delay": 2500,
    },
    {
        "name": "11_upcoming_contact",
        "title": "Upcoming DCs - Request Data",
        "section": "upcoming-dcs",
        "upcoming_tab": "contact",
        "scroll_to": "#upcomingTabContactContent",
        "wait_for": "#upcomingTabContactContent",
        "delay": 1500,
    },
]


SECTION_ID_MAP = {
    "home": "homeSection",
    "knowledge": "knowledgeSection",
    "pricing": "pricingSection",
    "services": "servicesSection",
    "existing-dcs": "existingDCsSection",
    "upcoming-dcs": "upcomingDCsSection",
}


async def switch_section(page, section_key: str):
    """Trigger in-page navigation to a section and wait for it to be active."""
    section_id = SECTION_ID_MAP.get(section_key)
    if not section_id:
        raise ValueError(f"Unknown section key: {section_key}")

    await page.evaluate(f"window.switchSection('{section_key}')")
    await page.wait_for_selector(f"#{section_id}.content-section.active", timeout=10_000)
    await page.wait_for_timeout(300)


async def show_existing_tab(page, tab_key: str):
    """Switch the Existing DCs tabs (heatmap/table/contact)."""
    await page.evaluate(f"window.showExistingTab('{tab_key}')")
    await page.wait_for_timeout(300)


async def show_upcoming_tab(page, tab_key: str):
    """Switch the Upcoming DCs tabs (heatmap/table/contact)."""
    await page.evaluate(f"window.showUpcomingTab('{tab_key}')")
    await page.wait_for_timeout(300)


async def scroll_to_selector(page, selector: str):
    """Scroll the page to bring a selector into view."""
    locator = page.locator(selector).first
    await locator.scroll_into_view_if_needed()
    await page.wait_for_timeout(200)


async def show_knowledge_tab(page, tab_key: str):
    """Switch the Knowledge tabs (glossary/handbook/taxonomy/studyguides)."""
    await page.evaluate(f"window.switchKnowledgeTab('{tab_key}')")
    await page.wait_for_timeout(400)


async def capture_screenshots():
    """Capture screenshots of all dashboard pages."""

    print("=" * 100)
    print("DC-INTEL DASHBOARD SNAPSHOT TOOL")
    print("=" * 100)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(OUTPUT_DIR, timestamp)
    os.makedirs(session_dir, exist_ok=True)
    thumb_dir = os.path.join(session_dir, "thumbnails")

    print(f"\nOutput directory: {session_dir}\n")

    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)  # Set to True for headless
        context = await browser.new_context(viewport=VIEWPORT_SIZE)
        page = await context.new_page()

        try:
            # Navigate to dashboard
            print(f"Loading dashboard: {DASHBOARD_URL}")
            await page.goto(DASHBOARD_URL, wait_until="networkidle")
            await asyncio.sleep(2)  # Initial load wait

            # Ensure client-side helpers exist before we start
            await page.wait_for_function(
                "typeof window.switchSection === 'function' && typeof window.showExistingTab === 'function' && typeof window.showUpcomingTab === 'function' && typeof window.switchKnowledgeTab === 'function'",
                timeout=10_000,
            )

            # Capture each page
            for page_config in PAGES:
                try:
                    name = page_config["name"]
                    title = page_config["title"]
                    scroll_to = page_config.get("scroll_to")
                    wait_for = page_config.get("wait_for", "body")
                    delay = page_config.get("delay", 0)
                    full_page = page_config.get("full_page", False)

                    print(f"\nCapturing: {title}")
                    print(f"   Scroll target: {scroll_to if scroll_to else 'top of page'}")

                    # Navigate to the correct section/tab
                    if page_config.get("section"):
                        await switch_section(page, page_config["section"])
                    if page_config.get("knowledge_tab"):
                        await show_knowledge_tab(page, page_config["knowledge_tab"])
                    if page_config.get("existing_tab"):
                        await show_existing_tab(page, page_config["existing_tab"])
                    if page_config.get("upcoming_tab"):
                        await show_upcoming_tab(page, page_config["upcoming_tab"])

                    # Wait for target content to be present
                    try:
                        await page.wait_for_selector(wait_for, timeout=10_000)
                        print("   Content loaded")
                    except Exception as e:
                        print(f"   Timeout waiting for content: {e}")

                    # Scroll to target (or top)
                    if scroll_to:
                        try:
                            await scroll_to_selector(page, scroll_to)
                            print("   Scrolled to section")
                        except Exception as e:
                            print(f"   Could not scroll to section: {e}")
                    else:
                        await page.evaluate("window.scrollTo(0, 0)")

                    # Additional delay for dynamic content
                    await asyncio.sleep(delay / 1000)

                    # Take screenshot (full page for the full view; viewport for sections)
                    screenshot_path = os.path.join(session_dir, f"{name}.png")
                    await page.screenshot(path=screenshot_path, full_page=full_page)

                    file_size_kb = os.path.getsize(screenshot_path) / 1024
                    print(f"   Screenshot saved: {os.path.basename(screenshot_path)} ({file_size_kb:.1f} KB)")
                except Exception as e:
                    # Fallback: still capture something so the file exists
                    fallback_path = os.path.join(session_dir, f"{page_config.get('name', 'unknown')}_fallback.png")
                    print(f"   Error capturing {page_config.get('name')}: {e}")
                    print("   Taking fallback full-page screenshot...")
                    try:
                        await page.screenshot(path=fallback_path, full_page=True)
                        print(f"   Fallback saved: {os.path.basename(fallback_path)}")
                    except Exception as e2:
                        print(f"   Fallback also failed: {e2}")
                    continue

            # Also create thumbnails (smaller versions)
            print("\n\nCreating thumbnails...")
            os.makedirs(thumb_dir, exist_ok=True)

            # Resize viewport for thumbnails
            await context.set_viewport_size({"width": 1280, "height": 720})
            await page.goto(DASHBOARD_URL, wait_until="networkidle")
            await asyncio.sleep(2)

            for page_config in PAGES:
                name = page_config["name"]
                scroll_to = page_config.get("scroll_to")
                try:
                    # Ensure helpers are ready for each loop
                    await page.wait_for_function(
                        "typeof window.switchSection === 'function' && typeof window.showExistingTab === 'function' && typeof window.showUpcomingTab === 'function' && typeof window.switchKnowledgeTab === 'function'",
                        timeout=10_000,
                    )

                    if page_config.get("section"):
                        await switch_section(page, page_config["section"])
                    if page_config.get("knowledge_tab"):
                        await show_knowledge_tab(page, page_config["knowledge_tab"])
                    if page_config.get("existing_tab"):
                        await show_existing_tab(page, page_config["existing_tab"])
                    if page_config.get("upcoming_tab"):
                        await show_upcoming_tab(page, page_config["upcoming_tab"])
                except Exception as e:
                    print(f"   Skipping thumbnail for {name}: {e}")
                    continue

                if scroll_to:
                    try:
                        await scroll_to_selector(page, scroll_to)
                    except Exception:
                        pass
                else:
                    await page.evaluate("window.scrollTo(0, 0)")

                await asyncio.sleep(0.5)

                thumb_path = os.path.join(thumb_dir, f"{name}_thumb.png")
                try:
                    await page.screenshot(path=thumb_path, full_page=False)
                    print(f"   Thumbnail: {os.path.basename(thumb_path)}")
                except Exception as e:
                    print(f"   Thumbnail failed for {name}: {e}")

        finally:
            await browser.close()

    print("\n" + "=" * 100)
    print("SUCCESS! Dashboard snapshots captured")
    print("=" * 100)
    print(f"\nFull screenshots: {session_dir}")
    print(f"Thumbnails: {thumb_dir}")
    print(f"\nTotal files: {len(os.listdir(session_dir)) + len(os.listdir(thumb_dir))}")
    print("=" * 100)


async def main():
    """Main entry point."""
    print("\nNOTE: Make sure the dashboard server is running!")
    print("      Run START_DASHBOARD.bat first if you haven't already.\n")

    response = input("Is the dashboard server running at http://localhost:8080? (y/n): ")
    if response.lower() != "y":
        print("\nPlease start the dashboard server first:")
        print("  1. Run START_DASHBOARD.bat")
        print("  2. Wait for browser to open")
        print("  3. Then run this script again")
        return

    await capture_screenshots()


if __name__ == "__main__":
    asyncio.run(main())
