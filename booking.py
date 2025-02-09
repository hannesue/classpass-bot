import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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

job = jobs[0]  # Execute the latest job
print(f"🚀 Booking {job['class_name']} at {job['studio']} on {job['date']} at {job['time']}")

# Set up WebDriver for Sauce Labs **with High Resolution**
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--window-size=1920,1080")  # Ensures all elements are visible
driver = webdriver.Remote(command_executor=SAUCE_URL, options=options)

try:
    # ✅ 1. LOGIN PROCESS
    print("🚀 Logging into ClassPass")
    driver.get("https://classpass.com/login")
    time.sleep(5)  # Allow login page to load

    driver.find_element(By.ID, "email").send_keys(job["email"])
    driver.find_element(By.ID, "password").send_keys(job["password"])
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    print("✅ Login attempt submitted")
    time.sleep(5)

    # **Verify Successful Login**
    if "dashboard" in driver.current_url:
        print("✅ Successfully redirected to Dashboard!")
    else:
        print("❌ Login failed! Not redirected to dashboard.")
        exit()

    # ✅ 2. NAVIGATE TO STUDIO PAGE
    print(f"🌍 Navigating to Studio: {job['studio_url']}")
    driver.get(job["studio_url"])
    time.sleep(5)

    # **Verify Studio Page Loaded**
    if job["studio_url"] not in driver.current_url:
        print(f"❌ Failed to load Studio Page! Current URL: {driver.current_url}")
        exit()

    # ✅ 3. SCROLL DOWN SLIGHTLY
    driver.execute_script("window.scrollBy(0, 500);")  # Scroll to reveal schedule
    print("📜 Scrolling down slightly to reveal class schedule...")
    time.sleep(2)

    # ✅ 4. FIND DATE
    print(f"📅 Searching for date: {job['date']}")
    while True:
        current_date = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']").text.strip()
        if current_date == job["date"]:
            print("✅ Correct date found!")
            break
        driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
        time.sleep(2)

    # ✅ 5. FIND TIME ELEMENT FIRST (STRICTLY WITHIN SECTION)
    print(f"🔍 Searching for time: {job['time']}")
    try:
        time_elements = driver.find_elements(By.XPATH, f"//span[contains(text(), '{job['time']}')]")

        if not time_elements:
            print(f"❌ No class found at {job['time']}. Exiting...")
            exit()

        time_element = time_elements[0]  # Take the first matching element
        print("✅ Found time element!")

    except NoSuchElementException:
        print(f"❌ Time {job['time']} not found!")
        exit()

    # ✅ 6. FIND CLASS AT THE SPECIFIED TIME
    print(f"🔍 Searching for class: {job['class_name']} at {job['time']}")
    try:
        # Get the parent section containing the time
        section = time_element.find_element(By.XPATH, "./ancestor::section")

        # Verify if class name is in this section
        if job["class_name"] in section.text:
            print("✅ Class found at this time!")

            # ✅ Scroll to the correct section before clicking
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section)
            time.sleep(2)

            # ✅ Find the booking button **strictly inside the correct section**
            book_button = section.find_element(By.XPATH, ".//button[contains(@data-qa, 'Schedule.cta')]")
            print("📌 Clicking the correct booking button now...")
            book_button.click()
            print("✅ Booking button clicked!")

        else:
            print("❌ Class not found at the specified time. Exiting...")
            exit()

    except NoSuchElementException:
        print("❌ Could not find class booking button!")
        exit()

    # ✅ 7. CONFIRM RESERVATION
    print("📌 Confirming reservation")
    time.sleep(3)  # Wait for confirmation screen to load

    # **Handle Different Confirmation Buttons**
    try:
        confirm_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-qa='Inquiry.reserve-button']"))
        )
        confirm_button.click()
        print("✅ Booking confirmed!")
    except TimeoutException:
        print("❌ Could not find standard confirmation button, trying alternative method...")
        try:
            confirm_button_alt = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm')]")
            confirm_button_alt.click()
            print("✅ Booking confirmed (alternative method)!")
        except:
            print("❌ Booking confirmation failed!")

    # ✅ 8. REMOVE COMPLETED JOB FROM jobs.json
    jobs.remove(job)
    with open("jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)
    print("✅ Job removed from jobs.json")

    print("✅ Test Completed")

except Exception as e:
    print(f"❌ Booking failed: {e}")

finally:
    driver.quit()
