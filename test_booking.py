import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Get credentials securely from GitHub Actions secrets
SAUCE_USERNAME = "oauth-hannes.ueberschaer-158e3"
SAUCE_ACCESS_KEY = "fc209d59-4f3d-4dc9-aefe-85295608343a"

# ✅ Sauce Labs Remote WebDriver URL
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com:443/wd/hub"

# ✅ Set up the desired capabilities for running on Sauce Labs
capabilities = {
    "browserName": "chrome",
    "browserVersion": "latest",
    "platformName": "Windows 10",
    "sauce:options": {}
}

# ✅ Open Sauce Labs Remote Browser
print("🚀 Connecting to Sauce Labs...")
driver = webdriver.Remote(command_executor=SAUCE_URL, desired_capabilities=capabilities)

# ✅ ClassPass Login Details
CLASS_PASS_URL = "https://classpass.com/login"
EMAIL = os.getenv("CLASSPASS_EMAIL")  # Store email in GitHub Secrets
PASSWORD = os.getenv("CLASSPASS_PASSWORD")  # Store password in GitHub Secrets

# ✅ Booking Details
STUDIO_URL = "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt"
CLASS_NAME = "RIDE45"
BOOKING_DATE = "Sun, Feb 2"
BOOKING_TIME = "7:15 AM"

try:
    # ✅ Step 1: Open ClassPass
    print("🚀 Navigating to ClassPass Login Page")
    driver.get(CLASS_PASS_URL)
    driver.maximize_window()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))

    # ✅ Step 2: Log In
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(EMAIL)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)

    print("✅ Logged in successfully")
    time.sleep(5)  # Wait for login to complete

    # ✅ Step 3: Open Studio URL
    print(f"🚀 Opening Studio: {STUDIO_URL}")
    driver.get(STUDIO_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # ✅ Step 4: Navigate to the correct date
    print("📌 Checking available dates on the page...")
    date_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'DateBar-date')]"))
    )
    current_date = date_element.text.strip()

    while current_date != BOOKING_DATE:
        if current_date < BOOKING_DATE:
            # Click "Next Day" button
            next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next day')]")
            next_button.click()
        else:
            # Click "Previous Day" button
            prev_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Previous day')]")
            prev_button.click()

        time.sleep(2)
        date_element = driver.find_element(By.XPATH, "//button[contains(@class, 'DateBar-date')]")
        current_date = date_element.text.strip()

    print(f"✅ Date selected: {current_date}")

    # ✅ Step 5: Find and Book the Class
    print(f"🔍 Searching for class: {CLASS_NAME} at {BOOKING_TIME}")
    class_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Schedule-class')]")

    for class_element in class_elements:
        class_title = class_element.find_element(By.XPATH, ".//h3").text.strip()
        class_time = class_element.find_element(By.XPATH, ".//time").text.strip()

        if class_title == CLASS_NAME and class_time == BOOKING_TIME:
            print("✅ Class found! Clicking 'Book' button...")
            book_button = class_element.find_element(By.XPATH, ".//button[contains(text(), 'credits')]")
            book_button.click()
            break
    else:
        print("❌ Class Not Found")

    # ✅ Step 6: Confirm Booking
    confirm_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Confirm')]"))
    )
    confirm_button.click()
    print("✅ Booking Completed!")

except Exception as e:
    print(f"❌ Booking failed: {e}")

finally:
    print("✅ Test Completed")
    driver.quit()
