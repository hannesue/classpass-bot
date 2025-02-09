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
    ### ✅ 1. LOGIN PROCESS
    print("🚀 Logging into ClassPass")
    driver.get("https://classpass.com/login")
    time.sleep(3)  # Allow login page to load

    driver.find_element(By.ID, "email").send_keys(job["email"])
    driver.find_element(By.ID, "password").send_keys(job["password"])
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    print("✅ Login attempt submitted")

    ### ✅ 2. WAIT FOR LOGIN TO COMPLETE
    WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))
    print(f"✅ Redirected to Dashboard! Current URL: {driver.current_url}")

    ### 🔴 DEBUG: PRINT WHAT PAGE WE ARE ON
    time.sleep(3)  # Allow page to stabilize
    print(f"🔍 After login, current page is: {driver.current_url}")

    ### ❌ STOP IF DASHBOARD NOT REACHED
    if "dashboard" not in driver.current_url:
        print(f"❌ ERROR: Expected Dashboard but got {driver.current_url}")
        exit()

    ### ✅ 3. NAVIGATE TO STUDIO PAGE (FIX)
    print(f"🌍 Navigating to Studio: {job['studio_url']}")
    driver.get(job["studio_url"])
    time.sleep(5)  # Allow page to load

    ### 🔴 DEBUG: PRINT PAGE AFTER NAVIGATION
    print(f"🔍 After navigating to studio, current page is: {driver.current_url}")

    ### ❌ STOP IF STUDIO PAGE NOT REACHED
    if job["studio_url"] not in driver.current_url:
        print(f"❌ ERROR: Expected {job['studio_url']} but got {driver.current_url}")
        print("🔄 Retrying studio navigation...")
        driver.get(job["studio_url"])  # Try again
        time.sleep(5)
        print(f"🔍 After retry, current page is: {driver.current_url}")

        # Final check
        if job["studio_url"] not in driver.current_url:
            print("❌ Failed to reach studio page. Exiting...")
            exit()

    print("✅ Successfully loaded the studio page!")

    ### ✅ 4. SCROLL DOWN SLIGHTLY
    driver.execute_script("window.scrollBy(0, 500);")  # Scroll to reveal schedule
    print("📜 Scrolling down slightly to reveal class schedule...")
    time.sleep(2)

    ### ✅ 5. FIND DATE
    print(f"📅 Searching for date: {job['date']}")
    while True:
        current_date = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']").text.strip()
        if current_date == job["date"]:
            print("✅ Correct date found!")
            break
        driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
        time.sleep(2)

    ### ✅ 6. FIND TIME ELEMENT
    print(f"🔍 Searching for time: {job['time']}")
    time_elements = driver.find_elements(By.XPATH, f"//span[contains(text(), '{job['time']}')]")

    if not time_elements:
        print(f"❌ No class found at {job['time']}. Exiting...")
        exit()

    time_element = time_elements[0]  # Take the first matching element
    print("✅ Found time element!")

    ### ✅ 7. FIND CLASS AT THE SPECIFIED TIME
    print(f"🔍 Searching for class: {job['class_name']} at {job['time']}")
    section = time_element.find_element(By.XPATH, "./ancestor::section")

    ### **DEBUG: PRINT ENTIRE SECTION TEXT BEFORE CLICKING BUTTON**
    print(f"🔍 Section text where time was found:\n{section.text}")

    ### ✅ Verify if class name is in this section
    class_elements = section.find_elements(By.XPATH, ".//span[contains(text(), '{}')]".format(job["class_name"]))
    if class_elements:
        print("✅ Class found at this time!")

        ### ✅ Scroll to the correct section before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section)
        time.sleep(2)

        ### ✅ Find the booking button **inside the correct section**
        book_buttons = section.find_elements(By.XPATH, ".//button[contains(@data-qa, 'Schedule.cta')]")

        if book_buttons:
            book_button = book_buttons[0]  # Take the first button inside the section
            print(f"📌 Booking Button found inside this section: {book_button.text}")
            print("✅ Clicking the correct booking button now...")
            book_button.click()
            print("✅ Booking button clicked!")
        else:
            print("❌ No booking button found in this section!")

    else:
        print("❌ Class not found at the specified time. Exiting...")
        exit()

    ### ✅ 8. CONFIRM RESERVATION
    print("📌 Confirming reservation")
    time.sleep(3)

    ### **Handle Different Confirmation Buttons**
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

    print("✅ Test Completed")

except Exception as e:
    print(f"❌ Booking failed: {e}")

finally:
    driver.quit()
