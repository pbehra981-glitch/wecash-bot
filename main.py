import random
import time
import csv
import os
import urllib.request
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"
TOTAL_ACCOUNTS = 1
PROXY_API_URL = ""
SCREENSHOT_DIR = "bot_screenshots"

def log_print(message):
    print(message, flush=True)

def take_screenshot(page, step_name):
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    timestamp = datetime.now().strftime("%H%M%S")
    filepath = os.path.join(SCREENSHOT_DIR, f"{step_name}_{timestamp}.png")
    try:
        page.screenshot(path=filepath, full_page=True)
        log_print(f"📸 Screenshot saved: {filepath}")
    except Exception as e:
        log_print(f"⚠️ Failed to take screenshot: {e}")

def generate_email():
    names = ["deepak", "rohit", "amit", "manish", "rahul", "pooja", "neha"]
    return f"{random.choice(names)}.{random.choice(names)}{random.randint(100, 999)}@gmail.com"

def save_to_csv(email, password, status):
    filename = "successful_accounts.csv"
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Email", "Password", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, status])

def main():
    log_print("🚀 Starting Stealth Anti-Bot Bypass WeCash Bot...")
    
    with sync_playwright() as p:
        for i in range(TOTAL_ACCOUNTS):
            log_print(f"\n--- Account {i+1} of {TOTAL_ACCOUNTS} ---")
            email = generate_email()
            password = "00000000"
            log_print(f"Generated Email: {email}")
            
            # STEALTH BROWSER LAUNCH (Bypassing Cloud/Headless Detection)
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-infobars",
                    "--disable-gpu",
                    "--window-size=1366,768",
                    "--start-maximized",
                    "--disable-setuid-sandbox",
                    "--no-first-run",
                    "--no-service-autorun",
                    "--password-store=basic",
                    "--use-mock-keychain"
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale="en-US",
                timezone_id="Asia/Kolkata"
            )
            
            # Inject stealth script to hide webdriver property completely from website
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {},
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            page = context.new_page()
            
            success = False
            for attempt in range(3):
                try:
                    log_print(f"Step 1: Opening Link (Attempt {attempt+1})...")
                    page.goto(REFERRAL_LINK, timeout=60000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    take_screenshot(page, "01_referral_loaded")
                    success = True
                    break
                except Exception as net_err:
                    log_print(f"⚠️ Network issue: {net_err}. Retrying...")
                    time.sleep(3)
            
            if not success:
                log_print(f"❌ Account {i+1} failed due to network error.")
                save_to_csv(email, password, "Failed - Network Error")
                take_screenshot(page, "ERROR_network")
                browser.close()
                continue
            
            try:
                # Step 2: Main page email & trigger
                log_print("Step 2: Entering email on main page...")
                page.fill("input[placeholder*='Email'], input[type='email']", email)
                time.sleep(1.5)
                take_screenshot(page, "02_email_filled")
                
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(4)
                take_screenshot(page, "03_clicked_signup_trigger")
                
                # Step 3: Modal credentials
                log_print("Step 3: Inside Modal - Entering email & password...")
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                time.sleep(1)
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(1)
                take_screenshot(page, "04_modal_credentials_filled")
                
                # Step 4 & 5: Force-Enable & Click Sign Up Button via Stealth JS
                log_print("Step 4 & 5: Forcing button activation via stealth evaluation...")
                page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'));
                        buttons.forEach(btn => {
                            btn.removeAttribute('disabled');
                            btn.classList.remove('disabled');
                            const txt = (btn.innerText || '').toLowerCase();
                            if (txt.includes('sign up') && !txt.includes('google')) {
                                btn.click();
                            }
                        });

                        const form = document.querySelector('form');
                        if (form) {
                            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                            form.dispatchEvent(submitEvent);
                        }
                    }
                """)
                
                log_print("Waiting for dashboard to load after signup...")
                time.sleep(12) 
                take_screenshot(page, "06_after_signup_attempt")
                
                # Scroll down safely
                log_print("Step 5.5: Scrolling down to Survey Partners...")
                page.evaluate("window.scrollBy(0, 800);")
                time.sleep(3)

                # Step 6: BitLabs Click
                log_print("Step 6: Locating and clicking BitLabs survey card...")
                clicked_survey = False
                for attempt in range(4):
                    try:
                        clicked_survey = page.evaluate("""
                            () => {
                                const elements = Array.from(document.querySelectorAll('div, a, span, button, p, h3'));
                                const bitlabsEl = elements.find(el => (el.innerText || '').trim().includes('BitLabs') && el.offsetParent !== null);
                                if (bitlabsEl) {
                                    bitlabsEl.scrollIntoView({behavior: 'smooth', block: 'center'});
                                    bitlabsEl.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        if clicked_survey:
                            log_print("✅ Successfully clicked BitLabs!")
                            break
                    except:
                        pass
                    time.sleep(3)
                
                if not clicked_survey:
                    take_screenshot(page, "ERROR_bitlabs_not_found")
                    raise Exception("BitLabs card could not be found or clicked.")

                log_print("Waiting for BitLabs popup modal...")
                time.sleep(8)
                take_screenshot(page, "07_bitlabs_modal_opened")

                save_to_csv(email, password, "Success - Task Triggered")
                log_print(f"🎉 Account {i+1} completed successfully!")
                
            except Exception as e:
                log_print(f"❌ Error caught in Account {i+1}: {e}")
                save_to_csv(email, password, f"Failed - {str(e)}")
                take_screenshot(page, "ERROR_EXCEPTION_STATE")
            finally:
                time.sleep(3)
                browser.close()
                
        log_print("--- Task Complete! ---")

if __name__ == "__main__":
    main()
