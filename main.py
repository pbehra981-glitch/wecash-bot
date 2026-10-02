import random
import time
import csv
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"
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
    names = ["deepak", "rohit", "amit", "manish", "rahul", "pooja", "neha", "vikash", "sunil", "ankit"]
    return f"{random.choice(names)}.{random.choice(names)}{random.randint(1000, 9999)}@gmail.com"

def save_to_csv(email, password, status):
    filename = "successful_accounts.csv"
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Email", "Password", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, status])

def main():
    log_print("🚀 Starting Guaranteed Checkbox WeCash Bot...")
    
    with sync_playwright() as p:
        log_print("\n--- Test Account Started ---")
        email = generate_email()
        password = "00000000"
        log_print(f"Generated Email: {email}")
        
        browser = p.chromium.launch(
            headless=True,
            slow_mo=50,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()
        
        success = False
        for attempt in range(3):
            try:
                log_print(f"Opening referral link (Attempt {attempt+1})...")
                page.goto(REFERRAL_LINK, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=15000)
                take_screenshot(page, "01_referral_loaded")
                success = True
                break
            except Exception as e:
                log_print(f"⚠️ Network retry error: {e}")
                time.sleep(5)
        
        if not success:
            save_to_csv(email, password, "Failed - Network Error")
            browser.close()
            log_print("❌ Test failed due to network error.")
            return
        
        try:
            # Signup steps
            log_print("Filling email & clicking initial signup...")
            page.wait_for_selector("input[placeholder*='Email'], input[type='email']", timeout=15000)
            page.fill("input[placeholder*='Email'], input[type='email']", email)
            time.sleep(2)
            take_screenshot(page, "02_email_filled")
            page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
            time.sleep(3)
            take_screenshot(page, "03_clicked_signup")
            
            try:
                page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
            except:
                pass
            
            page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
            time.sleep(2)
            take_screenshot(page, "04_password_filled")
            
            # --- GUARANTEED CHECKBOX CLICK FIX ---
            log_print("Clicking terms checkbox...")
            try:
                page.locator("input[type='checkbox']").click(force=True)
            except Exception as e:
                log_print(f"Checkbox direct click fallback: {e}")
                page.evaluate("""
                    () => {
                        const cb = document.querySelector("input[type='checkbox']");
                        if (cb) {
                            cb.click();
                            cb.checked = true;
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                """)
            
            time.sleep(2)
            take_screenshot(page, "05_terms_agreed")
            
            # Sign Up Button submission
            log_print("Clicking final Sign Up button...")
            page.locator("button:has-text('Sign Up')").filter(has_not=page.locator("text=Google")).last.click(force=True, timeout=10000)

            log_print("Waiting for dashboard to load after signup...")
            time.sleep(15)
            take_screenshot(page, "06_dashboard_loaded")
            
            # BitLabs / Offerwall Task Click
            log_print("Searching for BitLabs / Task section...")
            page.evaluate("window.scrollBy(0, 800);")
            time.sleep(4)
            
            clicked_survey = False
            for attempt in range(6):
                try:
                    clicked_survey = page.evaluate("""
                        () => {
                            const elements = Array.from(document.querySelectorAll('div, a, span, button, p, h3'));
                            const target = elements.find(el => {
                                const txt = (el.innerText || '').trim();
                                return (txt.includes('BitLabs') || txt.includes('Survey') || txt.includes('Offers')) && el.offsetParent !== null;
                            });
                            if (target) {
                                target.scrollIntoView({behavior: 'smooth', block: 'center'});
                                target.click();
                                return true;
                            }
                            return false;
                        }
                    """)
                    if clicked_survey:
                        break
                except:
                    pass
                time.sleep(3)
            
            if not clicked_survey:
                raise Exception("BitLabs / Offerwall section not found on dashboard.")

            log_print("BitLabs / Offerwall opened successfully!")
            time.sleep(12)
            take_screenshot(page, "07_offerwall_opened")
            
            # Accept & Continue handler
            log_print("Handling Accept & Continue / Survey prompts...")
            for step in range(6):
                for frame in page.frames:
                    if "about:blank" in frame.url: continue
                    try:
                        frame.evaluate("""
                            () => {
                                const btns = Array.from(document.querySelectorAll('button, div, span'));
                                const btn = btns.find(b => {
                                    const t = (b.innerText || '').trim();
                                    return t.includes('Accept') || t.includes('Continue') || t.includes('Start');
                                });
                                if (btn) btn.click();
                            }
                        """)
                    except:
                        pass
                time.sleep(3)

            save_to_csv(email, password, "Success - Task Triggered")
            log_print("🎉 Test Account completed successfully with guaranteed checkbox fix!")
            
        except Exception as e:
            log_print(f"❌ Error in Test Account: {e}")
            save_to_csv(email, password, f"Failed - {str(e)}")
            take_screenshot(page, "ERROR_STATE")
        finally:
            time.sleep(3)
            browser.close()
            log_print("🏁 Script finished single run.")

if __name__ == "__main__":
    main()
