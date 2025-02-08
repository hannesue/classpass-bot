import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# File Paths
JOB_FILE = "jobs.json"

# Read scheduled jobs
try:
    with open(JOB_FILE, "r") as file:
        jobs = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    jobs = []

if not jobs:
    print("❌ No bookings found.")
    exit()

# Process each job
for job in jobs:
    print(f"🚀 Booking {job['class_name']} at {job['studio']} on {job['date']} at {job['time']}")

    # Set up WebDriver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Login
        print("🚀 Logging into ClassPass")
        driver.get("https://classpass.com/login")
        time.sleep(3)

        driver.find_element(By.ID, "email").send_keys(job["email"])
        driver.find_element(By.ID, "password").send_keys(job["password"])
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        print("✅ Logged in successfully")
        time.sleep(5)

        # Navigate to Studio
        print(f"🚀 Opening Studio: {job['studio']}")
        driver.get(job["studio_url"])
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

        print("✅ Booking Completed")

        # Remove booked job
        jobs.remove(job)
        with open(JOB_FILE, "w") as file:
            json.dump(jobs, file, indent=4)

    except Exception as e:
        print(f"❌ Booking failed: {e}")

    finally:
        driver.quit()
