from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Sauce Labs credentials (replace with your actual credentials)
SAUCE_USERNAME = "oauth-hannes.ueberschaer-158e3"
SAUCE_ACCESS_KEY = "fc209d59-4f3d-4dc9-aefe-85295608343a"
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

desired_capabilities = {
    "browserName": "chrome",
    "browserVersion": "latest",
    "platformName": "Windows 10",
    "sauce:options": {
        "screenResolution": "1920x1080"  # Set resolution to Full HD
    }
}


# Start WebDriver with high resolution
print("🚀 Connecting to Sauce Labs...")
driver = webdriver.Remote(
    command_executor=SAUCE_URL,
    desired_capabilities=desired_capabilities
)
wait = WebDriverWait(driver, 10)

def login():
    """ Logs into ClassPass """
    print("🚀 Navigating to ClassPass Login Page")
    driver.get("https://classpass.com/login")
    time.sleep(2)
    
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("your_email")
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("your_password")
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(Keys.RETURN)
    
    print("✅ Logged in successfully")
    time.sleep(5)  # Allow page to load

def navigate_to_studio():
    """ Navigates directly to the fitness studio """
    print("🚀 Opening Studio: Perpetua Fitness")
    driver.get("https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt")
    time.sleep(5)

def get_current_date():
    """ Extracts the currently selected date from the webpage """
    try:
        current_date_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa='DateBar.date']")))
        current_date_text = current_date_element.text.strip()
        print(f"🔍 Found Date: {current_date_text}")
        return current_date_text
    except Exception as e:
        print(f"❌ Could not get the current date: {e}")
        return None

def select_correct_date(target_date):
    """ Scrolls left/right until the target date is found """
    print("📌 Searching for date...")

    for _ in range(10):  # Avoid infinite loops
        current_date_text = get_current_date()

        if current_date_text is None:
            print("❌ No date found, stopping.")
            break

        if current_date_text == target_date:
            print("✅ Target date found!")
            return True

        try:
            if current_date_text < target_date:
                print("➡ Clicking 'Next Day'")
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next day']")))
                driver.execute_script("arguments[0].click();", next_button)
            else:
                print("⬅ Clicking 'Previous Day'")
                prev_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Previous day']")))
                driver.execute_script("arguments[0].click();", prev_button)

            time.sleep(2)  # Wait for the date to update
        except Exception as e:
            print(f"❌ Error moving to date: {e}")
            break

    print("❌ Could not find the target date.")
    return False

if __name__ == "__main__":
    try:
        login()
        navigate_to_studio()
        success = select_correct_date("Mon, Feb 3")  # Selecting February 3rd

        if success:
            print("🎯 Date selection successful!")
        else:
            print("❌ Date selection failed!")

        print("✅ Test Completed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

