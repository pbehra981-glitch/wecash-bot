import random
import time
import csv
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"

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
    log_print("🚀 Starting Optimized WeCash & BitLabs Task Bot...")
    
    account_counter = 1
    with sync_playwright() as p:
        while True:
            log_print(f"\n--- Account {account_counter} Started ---")
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
                    page.goto(REFERRAL_LINK, timeout=45000)
                    page.wait_for_load_state("networkidle", timeout=10000)
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
                time.sleep(1)
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(3)
                
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(1)
                
                # Checkbox Click securely
                log_print("Agreeing to terms...")
                page.evaluate("""
                    () => {
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        if (checkboxes.length > 0) {
                            checkboxes[0].click();
                        } else {
                            const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                            let node;
                            while (node = walkers.nextNode()) {
                                if (node.nodeValue && node.nodeValue.includes('I agree')) {
                                    node.parentElement.click();
                                    break;
                                }
                            }
                        }
                    }
                """)
                time.sleep(2)
                
                # Sign Up Button submission
                log_print("Submitting signup...")
                page.locator("div[class*='modal'] button, form button, [role='dialog'] button").filter(has_text="Sign Up").filter(has_not=page.locator("text=Google")).last.click(timeout=5000)
                log_print("Waiting for dashboard to load after signup...")
                time.sleep(10)  # Thoda zyada wait taaki account fully login ho jaye
                
                # BitLabs / Offerwall Task Click
                log_print("Searching for BitLabs / Task section...")
                page.evaluate("window.scrollBy(0, 800);")
                time.sleep(3)
                
                clicked_survey = False
                for attempt in range(5):
                    try:
                        # Multiple strategies to find BitLabs
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
                time.sleep(8)
                
                # Accept & Continue handler inside frames or main page
                log_print("Handling Accept & Continue / Survey prompts...")
                for step in range(5):
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            frame.evaluate("""
                                () => {
                                    const btns = Array.from(document.querySelectorAll('button, div, span'));
                                    const btn = btns.find(b => (b.innerText || '').includes('Accept') || (b.innerText || '').includes('Continue') || (b.innerText || '').includes('Start'));
                                    if (btn) btn.click();
                                }
                            """)
                        except:
                            pass
                    time.sleep(3)

                save_to_csv(email, password, "Success - Task Triggered")
                log_print(f"🎉 Account {account_counter} completed with tasks!")
                
            except Exception as e:
                log_print(f"❌ Error in Account {account_counter}: {e}")
                save_to_csv(email, password, f"Failed - {str(e)}")
            finally:
                time.sleep(3)
                browser.close()
                account_counter += 1
                
            time.sleep(5)

if __name__ == "__main__":
    main()
