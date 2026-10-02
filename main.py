import random
import time
import csv
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Proxy hata di gayi hai taaki direct fast connection rahe
REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"

def log_print(message):
    print(message, flush=True)

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
    log_print("🚀 Starting Proxy-Free Unlimited Bot...")
    
    account_counter = 1
    with sync_playwright() as p:
        while True:
            log_print(f"\n--- Account {account_counter} Started ---")
            email = generate_email()
            password = "00000000"
            log_print(f"Generated Email: {email}")
            
            browser = p.chromium.launch(
                headless=True,
                slow_mo=60,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
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
                    page.goto(REFERRAL_LINK, timeout=40000)
                    success = True
                    break
                except Exception as e:
                    log_print(f"⚠️ Network retry error: {e}")
                    time.sleep(3)
            
            if not success:
                save_to_csv(email, password, "Failed - Network Error")
                browser.close()
                account_counter += 1
                continue
            
            try:
                # Signup steps
                log_print("Filling email & clicking signup...")
                page.fill("input[placeholder*='Email'], input[type='email']", email)
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(2)
                
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(0.5)
                
                # Checkbox Click
                log_print("Agreeing to terms...")
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
                                            view: window, bubbles: true, cancelable: true,
                                            clientX: clickX, clientY: clickY
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
                
                # Sign Up Button
                log_print("Submitting signup...")
                page.locator("div[class*='modal'] button, form button, [role='dialog'] button").filter(has_text="Sign Up").filter(has_not=page.locator("text=Google")).last.click(timeout=5000)
                time.sleep(7)
                
                # BitLabs Click
                log_print("Searching for BitLabs...")
                page.evaluate("window.scrollBy(0, 600);")
                time.sleep(1.5)
                
                clicked_survey = False
                for attempt in range(3):
                    try:
                        bitlabs_locator = page.locator("text=BitLabs").first
                        if bitlabs_locator.is_visible(timeout=5000):
                            bitlabs_locator.scroll_into_view_if_needed()
                            bitlabs_locator.click(force=True, timeout=5000)
                            clicked_survey = True
                            break
                    except:
                        time.sleep(2)
                
                if not clicked_survey:
                    clicked_survey = page.evaluate("""
                        () => {
                            const elements = Array.from(document.querySelectorAll('div, a, span, button'));
                            const bitlabsEl = elements.find(el => (el.innerText || '').trim().includes('BitLabs') && el.offsetParent !== null);
                            if (bitlabsEl) {
                                bitlabsEl.scrollIntoView({behavior: 'smooth', block: 'center'});
                                bitlabsEl.click();
                                return true;
                            }
                            return false;
                        }
                    """)
                    if not clicked_survey:
                        raise Exception("BitLabs card not found.")

                log_print("BitLabs opened successfully!")
                time.sleep(6)
                
                # Accept & Continue handler
                log_print("Handling Accept & Continue...")
                for _ in range(8):
                    clicked_accept = False
                    try:
                        btn = page.locator("button:has-text('Accept & Continue')").first
                        if btn.is_visible(timeout=1000):
                            btn.click(force=True)
                            break
                    except:
                        pass
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            btn = frame.locator("button:has-text('Accept & Continue')").first
                            if btn.is_visible(timeout=1000):
                                btn.click(force=True)
                                clicked_accept = True
                                break
                        except:
                            pass
                    if clicked_accept: break
                    time.sleep(2)

                time.sleep(5)

                # Survey / Profile questions loop
                log_print("Completing profile steps...")
                for q_step in range(1, 11):
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            cont_btn = frame.locator("button:has-text('Continue'), button:has-text('Next')").first
                            if cont_btn.is_visible(timeout=500):
                                frame.evaluate("""
                                    () => {
                                        const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'));
                                        if (checkboxes.length > 0) { checkboxes[0].click(); return; }
                                        const options = Array.from(document.querySelectorAll('div, label, span')).filter(el => {
                                            const txt = (el.innerText || '').trim();
                                            return txt.length > 0 && txt.length < 30 && !txt.includes('Continue') && !txt.includes('Next');
                                        });
                                        if (options.length > 0) { options[0].click(); }
                                    }
                                """)
                                time.sleep(1)
                                if cont_btn.is_visible(timeout=1000):
                                    cont_btn.click(force=True)
                                    break
                        except:
                            pass
                    time.sleep(2)

                save_to_csv(email, password, "Success")
                log_print(f"🎉 Account {account_counter} completed successfully!")
                
            except Exception as e:
                log_print(f"❌ Error in Account {account_counter}: {e}")
                save_to_csv(email, password, f"Failed - {str(e)}")
            finally:
                time.sleep(2)
                browser.close()
                account_counter += 1
                
            time.sleep(5)

if __name__ == "__main__":
    main()
