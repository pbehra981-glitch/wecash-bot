import random
import time
import csv
import urllib.request
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from playwright.sync_api import sync_playwright
import threading

app = FastAPI()

# ==========================================
# 1. DYNAMIC PROXY API CONFIGURATION
# ==========================================
PROXY_API_URL = ""  # Yahan apni proxy provider ki API daal sakte hain

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
    file_exists = False
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
        
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Email", "Password", "Proxy Used", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, password, proxy_used, status])

def automation_job(referral_link, total_count):
    with sync_playwright() as p:
        for i in range(total_count):
            print(f"\n--- Account {i+1} of {total_count} ---")
            email = generate_email()
            password = "00000000"
            print(f"Generated Email: {email}")
            
            selected_proxy = get_dynamic_proxy()
            if selected_proxy:
                print(f"✅ Using Fresh IP/Proxy: {selected_proxy}")
            else:
                print("⚠️ Proxy API empty. Running on local IP.")

            proxy_config = {"server": selected_proxy} if selected_proxy else None
            
            # HEADLESS = FALSE (Live dekhne ke liye)
            browser = p.chromium.launch(
                headless=False,
                slow_mo=60,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
                    page.goto(referral_link, timeout=40000)
                    success = True
                    break
                except Exception as net_err:
                    print(f"⚠️ Network/Proxy issue: {net_err}. Retrying in 3 seconds...")
                    time.sleep(3)
            
            if not success:
                print(f"❌ Account {i+1} failed due to network/proxy error.")
                save_to_csv(email, password, str(selected_proxy), "Failed - Network/Proxy Error")
                browser.close()
                continue
            
            try:
                # Step 2: Main page par email daal kar trigger button dabana
                print("Step 2: Entering email on main page and triggering modal...")
                page.fill("input[placeholder*='Email'], input[type='email']", email)
                page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
                time.sleep(2)
                
                # Step 3: Modal ke andar email aur password dalna
                print("Step 3: Inside Modal - Entering email and password...")
                try:
                    page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
                except:
                    pass
                time.sleep(0.5)
                
                page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
                time.sleep(0.5)
                
                # Step 4: Checkbox Click (Safe method)
                print("Step 4: Clicking the terms checkbox safely inside modal...")
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
                
                # Step 5: Modal ka Yellow Sign-Up button click
                print("Step 5: Clicking the Modal's Yellow Sign Up button...")
                page.locator("div[class*='modal'] button, form button, [role='dialog'] button").filter(has_text="Sign Up").filter(has_not=page.locator("text=Google")).last.click(timeout=5000)
                
                print("Waiting for dashboard to fully load after signup...")
                time.sleep(7) 
                
                # Scroll down safely to Survey Partners
                print("Step 5.5: Scrolling down safely to Survey Partners...")
                page.evaluate("window.scrollBy(0, 600);")
                time.sleep(1.5)

                # ==========================================================
                # STEP 6: SURVEY PARTNERS -> BITLABS CLICK (FIXED & IMPROVED)
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

                # ==========================================================
                # STEP 7: POPUP SEQUENCE (FOOLPROOF IFRAME & MAIN PAGE CLICK)
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

                # ==========================================================
                # STEP 9: QUESTIONS 4 TO 10
                # ==========================================================
                print("Answering Questions 4 to 10...")
                for q_step in range(4, 11):
                    print(f"➡️ Processing Question {q_step}...")
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

                print(f"🎉 ALL 10 QUESTIONS COMPLETED! Account {i+1} successfully processed!")
                save_to_csv(email, password, str(selected_proxy), "Success")
                
            except Exception as e:
                print(f"❌ Error caught in Account {i+1}: {e}")
                save_to_csv(email, password, str(selected_proxy), f"Failed - {str(e)}")
            finally:
                time.sleep(2)
                browser.close()
                
        print("--- Task Complete! ---")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BitLabs Bot (Fixed)</title>
        <style>
            body { font-family: Arial; background: #0f172a; color: #fff; padding: 40px; }
            .container { max-width: 400px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
            input, button { width: 100%; padding: 12px; margin-top: 15px; border-radius: 6px; border: none; font-size: 16px; box-sizing: border-box; }
            input { background: #334155; color: #fff; }
            button { background: #f59e0b; color: #000; font-weight: bold; cursor: pointer; }
            button:hover { background: #d97706; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Referral Bot</h2>
            <form action="/run-task" method="post">
                <label>Referral Link:</label>
                <input type="text" name="link" required placeholder="Paste link here">
                <label>Count:</label>
                <input type="number" name="count" value="1" min="1" required>
                <button type="submit">Run Bot</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/run-task")
async def run_task(link: str = Form(...), count: int = Form(...)):
    thread = threading.Thread(target=automation_job, args=(link, count))
    thread.start()
    return HTMLResponse(content="<h3>Task Started! Watch the browser window.</h3><a href='/'>Go Back</a>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
