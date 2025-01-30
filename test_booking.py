from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Sauce Labs credentials (replace with your actual credentials)
SAUCE_USERNAME = "oauth-hannes.ueberschaer-158e3"
SAUCE_ACCESS_KEY = "fc209d59-4f3d-4dc9-aefe-85295608343a"
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

# Desired capabilities for Sauce Labs
sauce_options = {
    "screenResolution": "1920x1080",  # High resolution
    "name": "ClassPass Bot Test",  # Test name in Sauce Labs dashboard
    "build": "ClassPass_Test_Build"  # Optional build identifier
}

chrome_options = webdriver.ChromeOptions()
chrome_options.set_capability("sauce:options", sauce_options)

# Start WebDriver
print("🚀 Connecting to Sauce Labs...")
driver = webdriver.Remote(command_executor=SAUCE_URL, options=chrome_options)

def login():
    print("🚀 Navigating to ClassPass Login Page")
    driver.get("https://classpass.com/login")
    time.sleep(2)
    
    # Enter credentials and log in
    driver.find_element(By.ID, "email").send_keys("ueberschaer@google.com")
    driver.find_element(By.ID, "password").send_keys("Glorchen1992!")
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    
    print("✅ Logged in successfully")
    time.sleep(5)  # Wait for new page to load

def navigate_to_studio():
    print("🚀 Opening Studio: Perpetua Fitness")
    driver.get("https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt")
    time.sleep(5)

def select_correct_date(target_date):
    print("📌 Checking available dates on the page...")
    while True:
        try:
            current_date_element = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']")
            current_date_text = current_date_element.text.strip()
            print(f"🔍 Current date on page: {current_date_text}")
            
            if current_date_text == target_date:
                print("✅ Target date found!")
                break
            elif current_date_text < target_date:
                print("➡ Moving to Next Day")
                driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
            else:
                print("⬅ Moving to Previous Day")
                driver.find_element(By.XPATH, "//button[@aria-label='Previous day']").click()
            
            time.sleep(2)  # Wait for the page to update
        except Exception as e:
            print(f"❌ Error selecting date: {e}")
            break

if __name__ == "__main__":
    try:
        login()
        navigate_to_studio()
        select_correct_date("Mon, Feb 3")  # Selecting February 3rd
        print("✅ Test Completed")
    except Exception as e:
        print(f"❌ Booking failed: {e}")
    finally:
        driver.quit()


