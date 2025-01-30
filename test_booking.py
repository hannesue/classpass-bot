import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Test Credentials (Use Fake Data or GitHub Secrets)
TEST_EMAIL = "your-email@example.com"
TEST_PASSWORD = "your-password"

# Studio URL (Example: Perpetua Fitness)
STUDIO_URL = "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt"

# Target Class & Date
TARGET_CLASS = "RIDE45"
TARGET_DATE = "Thu, Feb 1"
TARGET_TIME = "7:15 AM"

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def login():
    """Logs into ClassPass using test credentials."""
    print("🚀 Navigating to ClassPass Login Page")
    driver.get("https://classpass.com/login")
    time.sleep(3)

    driver.find_element(By.ID, "email").send_keys(TEST_EMAIL)
    driver.find_element(By.ID, "password").send_keys(TEST_PASSWORD)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
    
    time.sleep(5)  # Wait for login to process
    print("✅ Logged in successfully")

def navigate_to_studio():
    """Navigates to the specified studio's class page."""
    print(f"🚀 Opening Studio: {STUDIO_URL}")
    driver.get(STUDIO_URL)
    time.sleep(5)

def select_correct_date(target_date_str):
    """Finds and selects the correct date on the ClassPass page."""
    while True:
        try:
            displayed_date_elem = driver.find_element(By.XPATH, "//button[contains(@class, 'DateBar-date')]")
            displayed_date_text = displayed_date_elem.text.strip()

            print(f"📅 Displayed Date: {displayed_date_text} | 🎯 Target Date: {target_date_str}")

            if displayed_date_text == target_date_str:
                print("✅ Correct date selected!")
                break

            displayed_date = datetime.strptime(displayed_date_text, "%a, %b %d")
            target_date = datetime.strptime(target_date_str, "%a, %b %d")

            if target_date > displayed_date:
                next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next day']")
                next_button.click()
            else:
                prev_button = driver.find_element(By.XPATH, "//button[@aria-label='Previous day']")
                prev_button.click()

            time.sleep(1.5)

        except Exception as e:
            print(f"❌ Error selecting date: {e}")
            break

def select_class(target_class, target_time):
    """Finds and clicks the correct class booking button."""
    print(f"🔍 Searching for class: {target_class} at {target_time}")

    try:
        class_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'class-card')]")

        for class_item in class_list:
            class_title = class_item.find_element(By.XPATH, ".//div[contains(@class, 'class-title')]").text.strip()
            class_time = class_item.find_element(By.XPATH, ".//div[contains(@class, 'class-time')]").text.strip()

            if class_title == target_class and class_time == target_time:
                print(f"✅ Class Found: {class_title} at {class_time}")
                class_item.find_element(By.XPATH, ".//button[contains(text(), 'credits')]").click()
                print("🎟️ Class Booking Attempted")
                return True

        print("❌ Class Not Found")
        return False

    except Exception as e:
        print(f"❌ Error selecting class: {e}")
        return False

# Run the automated booking process
try:
    login()
    navigate_to_studio()
    select_correct_date(TARGET_DATE)
    select_class(TARGET_CLASS, TARGET_TIME)
except Exception as e:
    print(f"❌ Test Failed: {e}")
finally:
    driver.quit()
    print("✅ Test Completed")
