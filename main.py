import random
import time
import os
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
    names = ["deepak", "rohit", "amit", "manish", "rahul", "pooja", "neha"]
    return f"{random.choice(names)}.{random.choice(names)}{random.randint(1000, 9999)}@gmail.com"

def main():
    log_print("🚀 Starting Bot with Exact Coordinate Checkbox Logic...")
    
    with sync_playwright() as p:
        email = generate_email()
        password = "00000000"
        log_print(f"Generated Email: {email}")
        
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--disable-gpu",
                "--window-size=1366,768"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Kolkata"
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)
        
        page = context.new_page()
        
        try:
            log_print("Step 1: Opening referral link...")
            page.goto(REFERRAL_LINK, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
            take_screenshot(page, "01_referral_loaded")
            
            log_print("Step 2: Entering email on main page...")
            page.fill("input[placeholder*='Email'], input[type='email']", email)
            time.sleep(1.5)
            take_screenshot(page, "02_email_filled")
            
            page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
            time.sleep(4)
            take_screenshot(page, "03_clicked_signup_trigger")
            
            log_print("Step 3: Filling modal credentials...")
            try:
                page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
            except:
                pass
            
            page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
            time.sleep(1.5)
            take_screenshot(page, "04_modal_credentials_filled")
            
            # Step 4: Checkbox Click (Safe coordinate method)
            log_print("Step 4: Clicking the terms checkbox safely inside modal...")
            page.evaluate("""
                () => {
                    const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                    let node;
                    while (node = walkers.nextNode()) {
                        if (node.nodeValue && node.nodeValue.includes('I agree to the')) {
                            const range = document.createRange();
                            range.selectNode(node);
                            const rect = range.getBoundingClientRect();
                            if (rect.width > 0) {
                                const clickX = rect.left - 18;
                                const clickY = rect.top + (rect.height / 2);
                                
                                const target = document.elementFromPoint(clickX, clickY);
                                if (target) {
                                    const clickEvent = new MouseEvent('click', {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true,
                                        clientX: clickX,
                                        clientY: clickY
                                    });
                                    target.dispatchEvent(clickEvent);
                                }
                                break;
                            }
                        }
                    }
                }
            """)
            time.sleep(2)
            take_screenshot(page, "05_checkbox_checked")
            
            # Step 5: Force enable & click Sign Up button
            log_print("Step 5: Forcing Sign Up button click...")
            page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
                    const signupBtn = buttons.find(b => {
                        const txt = (b.innerText || '').trim().toLowerCase();
                        return txt.includes('sign up') && !txt.includes('google');
                    });
                    if (signupBtn) {
                        signupBtn.removeAttribute('disabled');
                        signupBtn.classList.remove('disabled');
                        signupBtn.click();
                    }
                }
            """)
            
            log_print("Waiting for dashboard to load...")
            time.sleep(10)
            take_screenshot(page, "06_after_signup")
            log_print("🎉 Flow Executed Successfully!")
            
        except Exception as e:
            log_print(f"❌ Error encountered: {e}")
            take_screenshot(page, "ERROR_STATE")
        finally:
            browser.close()
            log_print("🏁 Browser closed.")

if __name__ == "__main__":
    main()
