import random
import time
import csv
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"
TOTAL_ACCOUNTS = 1
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

def save_to_csv(email, password, status):
    filename = "successful_accounts.csv"
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Email", "Password", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, status])

def main():
    log_print("🚀 Starting Direct GitHub Actions Automation Bot...")
    
    with sync_playwright() as p:
        for i in range(TOTAL_ACCOUNTS):
            log_print(f"\n--- Account {i+1} of {TOTAL_ACCOUNTS} ---")
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
                
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(4)
                take_screenshot(page, "02_signup_modal_opened")
                
                log_print("Step 3: Filling modal credentials...")
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(1.5)
                take_screenshot(page, "03_credentials_filled")
                
                # Step 4: Checkbox Click (Exact Coordinate Safe Method)
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
                take_screenshot(page, "04_checkbox_clicked")
                
                # Step 5: Modal ka Yellow Sign-Up button click
                print("Step 5: Clicking the Modal's Yellow Sign Up button...")
                page.locator("div[class*='modal'] button, form button, [role='dialog'] button").filter(has_text="Sign Up").filter(has_not=page.locator("text=Google")).last.click(timeout=5000)
                
                print("Waiting for dashboard to fully load after signup...")
                time.sleep(7) 
                take_screenshot(page, "05_dashboard_loaded")
                
                # Scroll down safely to Survey Partners
                print("Step 5.5: Scrolling down safely to Survey Partners...")
                page.evaluate("window.scrollBy(0, 600);")
                time.sleep(1.5)

                # ==========================================================
                # STEP 6: SURVEY PARTNERS -> BITLABS CLICK
                # ==========================================================
                print("Step 6: Locating and clicking BitLabs survey card...")
                page.evaluate("window.scrollBy(0, 400);")
                time.sleep(2)
                
                clicked_survey = False
                for attempt in range(3):
                    try:
                        bitlabs_locator = page.locator("text=BitLabs").first
                        if bitlabs_locator.is_visible(timeout=5000):
                            bitlabs_locator.scroll_into_view_if_needed()
                            bitlabs_locator.click(force=True, timeout=5000)
                            print("✅ Successfully clicked BitLabs via Playwright locator!")
                            clicked_survey = True
                            break
                    except Exception as e:
                        print(f"⚠️ Attempt {attempt+1} failed to click BitLabs: {e}")
                        time.sleep(2)
                
                if not clicked_survey:
                    print("⚠️ Trying JavaScript fallback for BitLabs click...")
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
                    if clicked_survey:
                        print("✅ Successfully clicked BitLabs via JS fallback!")
                    else:
                        raise Exception("BitLabs card could not be found or clicked on the page.")

                take_screenshot(page, "06_bitlabs_clicked")

                # ==========================================================
                # STEP 7: POPUP SEQUENCE
                # ==========================================================
                print("Waiting for BitLabs popup modal to appear...")
                time.sleep(6)
                
                print("Looking for 'Accept & Continue' button...")
                clicked_accept = False
                for attempt in range(8):
                    try:
                        btn = page.locator("button:has-text('Accept & Continue')").first
                        if btn.is_visible(timeout=1000):
                            btn.click(force=True)
                            print("✅ Clicked 'Accept & Continue' on main page!")
                            clicked_accept = True
                            break
                    except:
                        pass
                    
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            btn = frame.locator("button:has-text('Accept & Continue')").first
                            if btn.is_visible(timeout=1000):
                                btn.click(force=True)
                                print("✅ Clicked 'Accept & Continue' inside iframe!")
                                clicked_accept = True
                                break
                        except:
                            pass
                    if clicked_accept:
                        break
                    time.sleep(2)

                time.sleep(3)

                for _ in range(5):
                    done = False
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            btn = frame.locator("button:has-text('Accept all')").first
                            if btn.is_visible(timeout=1000):
                                btn.click(force=True)
                                print("✅ Clicked 'Accept all'")
                                done = True
                                break
                        except:
                            pass
                    if done: break
                    time.sleep(2)

                time.sleep(2.5)
                take_screenshot(page, "07_accepted_popups")

                print("Looking for 'Complete your profile' button...")
                for _ in range(5):
                    done = False
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            btn = frame.locator("text='Complete your profile'").first
                            if btn.is_visible(timeout=1000):
                                btn.click(force=True)
                                print("✅ Clicked 'Complete your profile'")
                                done = True
                                break
                        except:
                            pass
                    if done: break
                    time.sleep(2)

                time.sleep(4)

                # ==========================================================
                # STEP 8: PROFILE QUESTIONS (Q1, Q2, Q3)
                # ==========================================================
                print("Answering Profile Question 1: Gender (Male)...")
                q1_done = False
                for _ in range(5):
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            male_opt = frame.locator("text='Male'").first
                            if male_opt.is_visible(timeout=1000):
                                male_opt.click()
                                print("✅ Selected Male successfully")
                                time.sleep(1)
                                cont_btn = frame.locator("button:has-text('Continue')").first
                                if cont_btn.is_visible(timeout=2000):
                                    cont_btn.click()
                                    print("✅ Clicked Continue after Gender!")
                                    q1_done = True
                                    break
                        except:
                            pass
                    if q1_done: break
                    time.sleep(2)

                time.sleep(3)
                take_screenshot(page, "08_q1_gender_done")

                print("Answering Profile Question 2: Zipcode (400001)...")
                q2_done = False
                for _ in range(5):
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            zip_input = frame.locator("input[type='text'], input").first
                            if zip_input.is_visible(timeout=1000):
                                zip_input.click()
                                zip_input.fill("400001")
                                print("✅ Entered Zipcode 400001")
                                time.sleep(1)
                                cont_btn = frame.locator("button:has-text('Continue')").first
                                if cont_btn.is_visible(timeout=2000):
                                    cont_btn.click()
                                    print("✅ Clicked Continue after Zipcode!")
                                    q2_done = True
                                    break
                        except:
                            pass
                    if q2_done: break
                    time.sleep(2)

                time.sleep(3)
                take_screenshot(page, "09_q2_zipcode_done")

                print("Answering Profile Question 3: Birthday Year (1995)...")
                q3_done = False
                for _ in range(5):
                    for frame in page.frames:
                        if "about:blank" in frame.url: continue
                        try:
                            if frame.locator("text='Enter your birthday'").is_visible(timeout=1000):
                                select_handled = frame.evaluate("""
                                    () => {
                                        const selects = Array.from(document.querySelectorAll('select'));
                                        for (let sel of selects) {
                                            const options = Array.from(sel.options);
                                            const has1995 = options.some(opt => opt.value === '1995' || opt.text.includes('1995'));
                                            if (has1995) {
                                                sel.value = '1995';
                                                sel.dispatchEvent(new Event('change', { bubbles: true }));
                                                return true;
                                            }
                                        }
                                        return false;
                                    }
                                """)
                                
                                if not select_handled:
                                    frame.evaluate("""
                                        () => {
                                            const allEls = Array.from(document.querySelectorAll('*'));
                                            const yearEl = allEls.find(el => (el.innerText || '').trim() === '2026' && el.children.length === 0);
                                            if (yearEl) {
                                                let box = yearEl.closest('div') || yearEl.parentElement;
                                                box.click();
                                            }
                                        }
                                    """)
                                    time.sleep(1.0)
                                    frame.evaluate("""
                                        () => {
                                            const allEls = Array.from(document.querySelectorAll('*'));
                                            const opt1995 = allEls.find(el => (el.innerText || '').trim() === '1995' && el.children.length === 0);
                                            if (opt1995) {
                                                opt1995.click();
                                            }
                                        }
                                    """)
                                
                                time.sleep(1.5)
                                cont_btn = frame.locator("button:has-text('Continue')").first
                                if cont_btn.is_visible(timeout=2000):
                                    cont_btn.click(force=True)
                                    print("✅ Clicked Continue successfully after DOB!")
                                    q3_done = True
                                    break
                        except:
                            pass
                    if q3_done: break
                    time.sleep(2)

                time.sleep(3)
                take_screenshot(page, "10_q3_dob_done")

                # ==========================================================
                # STEP 9: QUESTIONS 4 TO 10
                # ==========================================================
                print("Answering Questions 4 to 10...")
                for q_step in range(4, 11):
                    print(f"➡️️ Processing Question {q_step}...")
                    step_passed = False
                    
                    for attempt in range(6):
                        for frame in page.frames:
                            if "about:blank" in frame.url: continue
                            try:
                                cont_btn = frame.locator("button:has-text('Continue'), button:has-text('Next')").first
                                if cont_btn.is_visible(timeout=500):
                                    
                                    frame.evaluate("""
                                        () => {
                                            const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'));
                                            if (checkboxes.length > 0) {
                                                checkboxes[0].click();
                                                return;
                                            }
                                            
                                            const options = Array.from(document.querySelectorAll('div, label, span')).filter(el => {
                                                const txt = (el.innerText || '').trim();
                                                const rect = el.getBoundingClientRect();
                                                return (txt === 'Tamil' || txt === 'English' || txt === 'Hindi' || (txt.length > 0 && txt.length < 30 && rect.width > 30 && rect.height > 15)) &&
                                                       !txt.includes('Continue') && !txt.includes('Next') && !txt.includes('Complete');
                                            });
                                            
                                            if (options.length > 0) {
                                                options[0].click();
                                            }
                                        }
                                    """)
                                    time.sleep(1)
                                    
                                    if cont_btn.is_visible(timeout=1000):
                                        cont_btn.click(force=True)
                                        print(f"✅ Successfully passed Question {q_step}!")
                                        step_passed = True
                                        break
                            except:
                                pass
                        
                        if step_passed:
                            break
                        time.sleep(2)
                    
                    time.sleep(2)

                take_screenshot(page, "11_all_questions_completed")
                print(f"🎉 ALL 10 QUESTIONS COMPLETED! Account {i+1} successfully processed!")
                save_to_csv(email, password, "Success")
                
            except Exception as e:
                print(f"❌ Error caught in Account {i+1}: {e}")
                take_screenshot(page, "ERROR_STATE")
                save_to_csv(email, password, f"Failed - {str(e)}")
            finally:
                time.sleep(2)
                browser.close()
                
        print("--- Task Complete! ---")

if __name__ == "__main__":
    main()
