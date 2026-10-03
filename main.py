import random
import time
import csv
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"
TOTAL_ACCOUNTS = 1

def log_print(message):
    print(message, flush=True)

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
    log_print("🚀 Starting Original WeCash Bot (Fixed Modal Wait)...")
    
    with sync_playwright() as p:
        for i in range(TOTAL_ACCOUNTS):
            log_print(f"\n--- Account {i+1} of {TOTAL_ACCOUNTS} ---")
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
                    success = True
                    break
                except Exception as e:
                    log_print(f"⚠️ Network retry error: {e}")
                    time.sleep(5)
            
            if not success:
                save_to_csv(email, password, "Failed - Network Error")
                browser.close()
                log_print("❌ Test failed due to network error.")
                continue
            
            try:
                # Signup steps
                log_print("Filling email & clicking initial signup...")
                page.wait_for_selector("input[placeholder*='Email'], input[type='email']", timeout=15000)
                page.fill("input[placeholder*='Email'], input[type='email']", email)
                time.sleep(2)
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                
                # IMPORTANT FIX: Extra wait for modal to fully pop up on cloud runner
                log_print("Waiting for popup modal to appear...")
                time.sleep(4)
                
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(2)
                
                # Original JS Checkbox & Signup Bypass
                log_print("Executing original JS checkbox check & signup click...")
                page.evaluate("""
                    () => {
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        if (checkboxes.length > 0) {
                            const cb = checkboxes[0];
                            cb.checked = true;
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                            cb.dispatchEvent(new Event('input', { bubbles: true }));
                        } else {
                            const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                            let node;
                            while (node = walkers.nextNode()) {
                                if (node.nodeValue && (node.nodeValue.includes('I agree') || node.nodeValue.includes('Terms'))) {
                                    node.parentElement.click();
                                    break;
                                }
                            }
                        }

                        setTimeout(() => {
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
                        }, 1000);
                    }
                """)
                
                log_print("Waiting for dashboard to load after signup...")
                time.sleep(15)
                
                # BitLabs Task Click
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
                log_print("🎉 Account completed successfully!")
                
            except Exception as e:
                log_print(f"❌ Error in Account: {e}")
                save_to_csv(email, password, f"Failed - {str(e)}")
            finally:
                time.sleep(3)
                browser.close()
                log_print("🏁 Script finished run.")

if __name__ == "__main__":
    main()
