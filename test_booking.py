from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

# 🔑 Sauce Labs Credentials (Directly in Code)
SAUCE_USERNAME = "oauth-hannes.ueberschaer-158e3"
SAUCE_ACCESS_KEY = "fc209d59-4f3d-4dc9-aefe-85295608343a"

# 🚀 Sauce Labs URL
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

# 🌍 Desired Capabilities for Chrome on Sauce Labs
capabilities = {
    "browserName": "chrome",
    "browserVersion": "latest",
    "platformName": "Windows 10",
    "sauce:options": {}
}

# 🚀 Connect to Sauce Labs
print("🚀 Connecting to Sauce Labs...")
driver = webdriver.Remote(command_executor=SAUCE_URL, options=webdriver.ChromeOptions())

try:
    # 🏁 Step 1: Open ClassPass Login Page
    print("🔗 Navigating to ClassPass Login Page...")
    driver.get("https://classpass.com/login")
    time.sleep(5)  # Allow page to load

    # ❌ Step 2: Close Any Popups
    try:
        close_popup = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
        close_popup.click()
        print("✅ Closed popup!")
        time.sleep(2)  # Give it time to close
    except:
        print("⚠️ No popup detected, proceeding...")

    # ✅ Step 3: Enter Email & Password
    print("🔑 Entering login credentials...")
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")

    email_input.send_keys("ueberschaer@google.com")
    password_input.send_keys("Glorchen1992!")
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for login to process

    # ✅ Step 4: Verify Login Success
    if "dashboard" in driver.current_url:
        print("✅ Login successful!")
    else:
        print("❌ Login failed! Check credentials.")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    # Close browser
    driver.quit()
    print("🚪 Browser closed.")
