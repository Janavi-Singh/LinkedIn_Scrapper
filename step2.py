import asyncio
import pandas as pd
import random
import os
from playwright.async_api import async_playwright

# ================= ⚙️ CONFIGURATION =================
INPUT_FILE = "step1_urls.csv"       
OUTPUT_FILE = "step2_dump.csv"
STATE_FILE = "linkedin_session.json"

LINKEDIN_EMAIL = "email"
LINKEDIN_PASSWORD = "pass"

DAILY_LIMIT = 50 

# ================= 🛠️ CORE LOGIC =================

async def scrape_full_text(page, url):
    print(f"--- 🔍 Scraping: {url} ---")
    
    try:
        # Increase timeout and wait for load
        await page.goto(url, wait_until="load", timeout=90000)
        
        # Give it a moment to breathe
        await asyncio.sleep(5)

        # Check for Security Check manually by looking for specific text
        if await page.get_by_text("Security Check").is_visible() or "checkpoint" in page.url:
            print("🛑 CAPTCHA DETECTED! Please solve it in the browser window NOW.")
            # Wait until the CAPTCHA is gone
            await page.wait_for_selector("h1", timeout=300000) 

        # Scroll to the bottom and back up to force everything to render
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, 0);")

        # --- EXTRACTION ---
        # 1. Try to get the Name, Headline, and Location with broad selectors
        name = await page.locator("h1").first.inner_text() if await page.locator("h1").count() > 0 else "N/A"
        
        headline = "N/A"
        if await page.locator(".text-body-medium").count() > 0:
            headline = await page.locator(".text-body-medium").first.inner_text()

        location = "N/A"
        if await page.locator(".text-body-small.inline").count() > 0:
            location = await page.locator(".text-body-small.inline").first.inner_text()

        # 2. THE MASTER DUMP (Everything visible on the page)
        # We grab the 'body' directly. This cannot fail if the page loaded.
        raw_text = await page.locator("body").inner_text()
        raw_dump = " ".join([line.strip() for line in raw_text.split('\n') if line.strip()])

        return {
            "LinkedIn URL": url,
            "Name": name.strip(),
            "Headline": headline.strip(),
            "Location": location.strip(),
            "About": "See Raw Dump",
            "Raw Text Dump": raw_dump,
            "Contact Info": "Locked/Hidden"
        }

    except Exception as e:
        # If all else fails, grab whatever text is currently on the screen
        print(f"   ⚠️ Timeout/Error on {url}. Capturing partial data...")
        try:
            raw_text = await page.locator("body").inner_text()
            raw_dump = " ".join([line.strip() for line in raw_text.split('\n') if line.strip()])
            return {
                "LinkedIn URL": url, "Name": "Timeout/Check Manual", "Headline": "N/A", 
                "Location": "N/A", "About": "N/A", "Raw Text Dump": raw_dump, "Contact Info": "Locked/Hidden"
            }
        except:
            return {
                "LinkedIn URL": url, "Name": "CRITICAL FAILURE", "Headline": "N/A", 
                "Location": "N/A", "About": "N/A", "Raw Text Dump": "N/A", "Contact Info": "Locked/Hidden"
            }

async def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return

    df_in = pd.read_csv(INPUT_FILE)
    urls = df_in['LinkedIn URL'].tolist()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        # Important: Set a large window size so LinkedIn doesn't serve the 'Mobile' version
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # Login
        await page.goto("https://www.linkedin.com/login")
        await page.fill("#username", LINKEDIN_EMAIL)
        await page.fill("#password", LINKEDIN_PASSWORD)
        await page.click("button[type='submit']")
        
        print("⏳ Waiting for login/feed... (Solve CAPTCHA if it appears)")
        await page.wait_for_url("**/feed/**", timeout=300000)

        results = []
        for i, url in enumerate(urls[:DAILY_LIMIT]):
            data = await scrape_full_text(page, url)
            results.append(data)
            
            # Instant Append to CSV
            pd.DataFrame([data]).to_csv(OUTPUT_FILE, mode='a', header=not os.path.exists(OUTPUT_FILE), index=False)
            
            print(f"✅ Record [{i+1}/{len(urls)}] Saved.")

            # Safety sleep to keep the account safe
            sleep_time = random.uniform(45, 75)
            print(f"💤 Sleeping {sleep_time:.1f}s...")
            await asyncio.sleep(sleep_time)

        await browser.close()
        print(f"--- 🎉 DONE. Results in {OUTPUT_FILE} ---")

if __name__ == "__main__":
    asyncio.run(main())
