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

# Read latest job
with open("jobs.json", "r") as file:
    jobs = json.load(file)

if not jobs:
    print("❌ No bookings found.")
    exit()

job = jobs[0]  # Only executing the latest job
print(f"🚀 Booking {job['class_name']} at {job['studio']} on {job['date']} at {job['time']}")

# Set up WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Remote(command_executor=SAUCE_URL, options=options)

try:
    # Login
    print("🚀 Logging into ClassPass")
    driver.get("https://classpass.com/login")
    time.sleep(3)

    driver.find_element(By.ID, "email").send_keys("ueberschaer@google.com")
    driver.find_element(By.ID, "password").send_keys("Glorchen1992!")
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    print("✅ Logged in successfully")
    time.sleep(5)

    # Navigate to Studio
    print(f"🚀 Opening Studio: {job['studio']}")
    driver.get(job["studio"])
    time.sleep(5)

    # Select Date
    print(f"📌 Finding Date: {job['date']}")
    while True:
        current_date = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']").text.strip()
        if current_date == job["date"]:
            print("✅ Date matched")
            break
        driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
        time.sleep(2)

    # Find & Book Class
    print(f"🔍 Looking for {job['class_name']} at {job['time']}")
    classes = driver.find_elements(By.XPATH, "//section[@data-component='Section']")

    for c in classes:
        if job["class_name"] in c.text and job["time"] in c.text:
            print("✅ Class found, booking...")
            c.find_element(By.XPATH, ".//button[@data-qa='Schedule.cta']").click()
            time.sleep(2)

            print("📌 Confirming reservation")
            driver.find_element(By.XPATH, "//button[@data-qa='Inquiry.reserve-button']").click()
            print("✅ Booking completed!")
            break

    print("✅ Test Completed")
except Exception as e:
    print(f"❌ Booking failed: {e}")
finally:
    driver.quit()

