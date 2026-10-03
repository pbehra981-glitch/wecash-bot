import random
import time
from playwright.sync_api import sync_playwright

REFERRAL_LINK = "https://wecashapp.com?inviteCode=PiQgs8J8swwMV2obCRDg"

def log_print(message):
    print(message, flush=True)

def generate_email():
    names = ["deepak", "rohit", "amit", "manish", "rahul", "pooja", "neha"]
    return f"{random.choice(names)}.{random.choice(names)}{random.randint(1000, 9999)}@gmail.com"

def main():
    log_print("🚀 Starting Minimal Signup Test...")
    
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
                "--disable-infobars"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        
        # Hide automation fingerprint
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        
        page = context.new_page()
        
        try:
            log_print("Step 1: Opening referral link...")
            page.goto(REFERRAL_LINK, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            log_print("Step 2: Entering email on main page & triggering modal...")
            page.fill("input[placeholder*='Email'], input[type='email']", email)
            time.sleep(1)
            page.click("button:has-text('Claim your gift'), button:has-text('Sign Up')")
            
            log_print("Step 3: Waiting for modal & filling credentials...")
            time.sleep(4) # Modal load hone ka proper wait
            
            try:
                page.locator(".modal input[type='email'], form input[type='email']").first.fill(email)
            except:
                pass
            
            page.locator(".modal input[type='password'], form input[type='password']").first.fill(password)
            time.sleep(1)
            
            log_print("Step 4: Clicking terms text/checkbox...")
            # Native click on terms text
            try:
                page.get_by_text("I agree to the").click(timeout=3000)
            except:
                page.evaluate("""
                    () => {
                        const cb = document.querySelector('input[type="checkbox"]');
                        if (cb) {
                            cb.checked = true;
                            cb.click();
                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                """)
            
            time.sleep(1)
            
            log_print("Step 5: Clicking Sign Up button...")
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
            
            log_print("Step 6: Waiting to check signup completion...")
            time.sleep(10)
            log_print("🎉 Base Signup Flow Finished!")
            
        except Exception as e:
            log_print(f"❌ Error encountered: {e}")
        finally:
            browser.close()
            log_print("🏁 Browser closed.")

if __name__ == "__main__":
    main()
