from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Sauce Labs credentials (replace with actual credentials)
SAUCE_USERNAME = "oauth-hannes.ueberschaer-158e3"
SAUCE_ACCESS_KEY = "fc209d59-4f3d-4dc9-aefe-85295608343a"
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

# Desired capabilities for Sauce Labs
desired_capabilities = {
    "browserName": "chrome",
    "browserVersion": "latest",
    "platformName": "Windows 10"
}

# Start WebDriver
print("🚀 Connecting to Sauce Labs...")
driver = webdriver.Remote(command_executor=SAUCE_URL, options=webdriver.ChromeOptions())
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to appear

def login():
    print("🚀 Navigating to ClassPass Login Page")
    driver.get("https://classpass.com/login")
    time.sleep(2)

    # Enter credentials and log in
    driver.find_element(By.ID, "email").send_keys("ueberschaer@google.com")
    driver.find_element(By.ID, "password").send_keys("Glorchen1992!")
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(Keys.RETURN)

    print("✅ Logged in successfully")
    time.sleep(5)  # Allow page to load

def navigate_to_studio():
    print("🚀 Opening Studio: Perpetua Fitness")
    driver.get("https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt")
    time.sleep(5)

def get_current_date():
    """ Extracts the currently selected date from the page """
    try:
        current_date_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa='DateBar.date']")))
        return current_date_element.text.strip()
    except Exception as e:
        print(f"❌ Failed to get current date: {e}")
        return None

def select_correct_date(target_date):
    """ Navigates through dates until the correct one is selected """
    print("📌 Checking available dates on the page...")

    while True:
        current_date_text = get_current_date()
        
        if current_date_text is None:
            print("❌ Could not retrieve date, stopping.")
            break
        
        print(f"🔍 Current date on page: {current_date_text}")

        if current_date_text == target_date:
            print("✅ Target date found!")
            break

        try:
            if current_date_text < target_date:
                print("➡ Moving to Next Day")
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next day']")))
                next_button.click()
            else:
                print("⬅ Moving to Previous Day")
                prev_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Previous day']")))
                prev_button.click()

            time.sleep(2)  # Wait for the page to update
        except Exception as e:
            print(f"❌ Error moving to date: {e}")
            break

if __name__ == "__main__":
    try:
        login()
        navigate_to_studio()
        select_correct_date("Mon, Feb 3")  # Target date to select
        print("✅ Test Completed")
    except Exception as e:
        print(f"❌ Booking failed: {e}")
    finally:
        driver.quit()
