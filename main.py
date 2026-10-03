import random
import time
import csv
import os
import urllib.request
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"
TOTAL_ACCOUNTS = 1  # GitHub par test karne ke liye abhi 1 rakha hai, baad mein badha sakte hain
PROXY_API_URL = ""  # Agar proxy use karni ho toh yahan daal sakte hain

def get_dynamic_proxy():
    if not PROXY_API_URL:
        return None
    try:
        req = urllib.request.Request(PROXY_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            proxy_ip = response.read().decode('utf-8').strip()
            if proxy_ip:
                if not proxy_ip.startswith("http"):
                    return f"http://{proxy_ip}"
                return proxy_ip
    except Exception as e:
        print(f"⚠️ Proxy API Fetch Error: {e}")
    return None

def generate_email():
    names = ["deepak", "rohit", "amit", "manish", "rahul", "pooja", "neha"]
    return f"{random.choice(names)}.{random.choice(names)}{random.randint(100, 999)}@gmail.com"

def save_to_csv(email, password, proxy_used, status):
    filename = "successful_accounts.csv"
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Email", "Password", "Proxy Used", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, proxy_used, status])

def main():
    print("🚀 Starting Standalone WeCash GitHub Action Bot...")
    
    with sync_playwright() as p:
        for i in range(TOTAL_ACCOUNTS):
            print(f"\n--- Account {i+1} of {TOTAL_ACCOUNTS} ---")
            email = generate_email()
            password = "00000000"
            print(f"Generated Email: {email}")
            
            selected_proxy = get_dynamic_proxy()
            proxy_config = {"server": selected_proxy} if selected_proxy else None
            
            # HEADLESS = TRUE for GitHub Actions cloud runner
            browser = p.chromium.launch(
                headless=True,
                slow_mo=60,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-infobars"
                ]
            )
            
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ]
            
            context = browser.new_context(
                proxy=proxy_config,
                user_agent=random.choice(user_agents),
                viewport={"width": 1366, "height": 768}
            )
            page = context.new_page()
            
            success = False
            for attempt in range(3):
                try:
                    print(f"Step 1: Opening Link (Attempt {attempt+1})...")
                    page.goto(REFERRAL_LINK, timeout=60000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    success = True
                    break
                except Exception as net_err:
                    print(f"⚠️ Network issue: {net_err}. Retrying...")
                    time.sleep(3)
            
            if not success:
                print(f"❌ Account {i+1} failed due to network error.")
                save_to_csv(email, password, str(selected_proxy), "Failed - Network Error")
                browser.close()
                continue
            
            try:
                # Step 2: Main page par email daal kar trigger button dabana
                print("Step 2: Entering email on main page and triggering modal...")
                page.fill("input[placeholder*='Email'], input[type='email']", email)
                time.sleep(1)
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(3)
                
                # Step 3: Modal ke andar email aur password dalna
                print("Step 3: Inside Modal - Entering email and password...")
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                time.sleep(1)
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(1)
                
                # Step 4: Headless-Safe Checkbox Click Fix
                print("Step 4: Checking the terms checkbox safely via JS...")
                page.evaluate("""
                    () => {
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        if (checkboxes.length > 0) {
                            checkboxes[0].checked = true;
                            checkboxes[0].dispatchEvent(new Event('change', { bubbles: true }));
                            checkboxes[0].dispatchEvent(new Event('input', { bubbles: true }));
                        } else {
                            const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                            let node;
                            while (node = walkers.nextNode()) {
                                if (node.nodeValue && node.nodeValue.includes('I agree to the')) {
                                    node.parentElement.click();
                                    break;
                                }
                            }
                        }
                    }
                """)
                time.sleep(2)
                
                # Step 5: Modal ka Yellow Sign-Up button click (Bypassing disabled state)
                print("Step 5: Clicking the Modal's Sign Up button...")
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
                
                print("Waiting for dashboard to fully load after signup...")
                time.sleep(10) 
                
                # Scroll down safely to Survey Partners
                print("Step 5.5: Scrolling down safely to Survey Partners...")
                page.evaluate("window.scrollBy(0, 800);")
                time.sleep(3)

                # Step 6: BitLabs Click
                print("Step 6: Locating and clicking BitLabs survey card...")
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
                            print("✅ Successfully clicked BitLabs!")
                            break
                    except:
                        pass
                    time.sleep(3)
                
                if not clicked_survey:
                    raise Exception("BitLabs card could not be found or clicked.")

                print("Waiting for BitLabs popup modal to appear...")
                time.sleep(8)
                
                # Step 7: Accept & Continue handler inside frames or main page
                print("Handling Accept & Continue / Survey prompts...")
                for step in range(5):
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

                save_to_csv(email, password, str(selected_proxy), "Success - Task Triggered")
                print(f"🎉 Account {i+1} completed successfully!")
                
            except Exception as e:
                print(f"❌ Error caught in Account {i+1}: {e}")
                save_to_csv(email, password, str(selected_proxy), f"Failed - {str(e)}")
            finally:
                time.sleep(3)
                browser.close()
                
        print("--- Task Complete! ---")

if __name__ == "__main__":
    main()
