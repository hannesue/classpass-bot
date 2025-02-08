import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Sauce Labs credentials
SAUCE_USERNAME = "oauth-ueberschaergbr-dc0f3"
SAUCE_ACCESS_KEY = "78421343-d4ed-4a10-981f-6194ecfc7122"
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

# Read latest job from jobs.json
with open("jobs.json", "r") as file:
    jobs = json.load(file)

if not jobs:
    print("❌ No bookings found.")
    exit()

job = jobs[0]  # Only executing the latest job
print(f"🚀 Booking {job['class_name']} at {job['studio']} on {job['date']} at {job['time']}")

# Set up WebDriver for Sauce Labs with High Resolution
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Full-screen window
options.add_argument("--window-size=1920,1080")  # High resolution
driver = webdriver.Remote(command_executor=SAUCE_URL, options=options)

try:
    # ✅ 1. LOGIN PROCESS
    print("🚀 Logging into ClassPass")
    driver.get("https://classpass.com/login")
    time.sleep(3)  # Allow page to load

    driver.find_element(By.ID, "email").send_keys(job["email"])
    driver.find_element(By.ID, "password").send_keys(job["password"])
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    print("✅ Logged in successfully")
    time.sleep(5)  # Allow time for login redirect

    # ❗ CHECK IF LOGIN WAS SUCCESSFUL
    if "dashboard" not in driver.current_url:
        print("❌ Login failed! Not redirected to dashboard.")
        driver.quit()
        exit()

    # ✅ 2. NAVIGATE TO STUDIO PAGE
    print(f"🚀 Opening Studio: {job['studio']}")
    driver.get(job["studio_url"])
    time.sleep(5)

    # ✅ 3. SELECT DATE
    print(f"📌 Finding Date: {job['date']}")
    while True:
        current_date = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']").text.strip()
        if current_date == job["date"]:
            print("✅ Date matched")
            break
        driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
        time.sleep(2)

    # ✅ 4. FIND & BOOK CLASS
    print(f"🔍 Looking for {job['class_name']} at {job['time']}")
    classes = driver.find_elements(By.XPATH, "//section[@data-component='Section']")

    for c in classes:
        if job["class_name"] in c.text and job["time"] in c.text:
            print("✅ Class found, booking...")
            c.find_element(By.XPATH, ".//button[@data-qa='Schedule.cta']").click()
            time.sleep(2)

            # ✅ 5. CONFIRM BOOKING
            print("📌 Checking for confirmation button...")
            time.sleep(3)  # Wait for confirmation screen

            # DEBUG: PRINT ALL BUTTONS ON PAGE
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for b in buttons:
                print(f"🟢 Button found: {b.get_attribute('outerHTML')}")

            try:
                confirm_button = driver.find_element(By.XPATH, "//button[@data-qa='Inquiry.reserve-button']")
                confirm_button.click()
                print("✅ Booking confirmed!")
            except Exception as e:
                print(f"❌ Could not find 'Confirm' button via standard method: {e}")
                
                # ❗ Alternative booking confirmation
                try:
                    confirm_button_alt = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm')]")
                    confirm_button_alt.click()
                    print("✅ Booking confirmed (alternative method)!")
                except Exception as e:
                    print(f"❌ Alternative booking confirmation failed: {e}")

            break  # Exit loop after booking

    # ✅ 6. REMOVE COMPLETED JOB FROM jobs.json
    jobs.remove(job)
    with open("jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)
    print("✅ Job removed from jobs.json")

    print("✅ Test Completed")

except Exception as e:
    print(f"❌ Booking failed: {e}")

finally:
    driver.quit()
