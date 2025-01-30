from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Sauce Labs credentials
SAUCE_USERNAME = "oauth-ueberschaergbr-dc0f3"
SAUCE_ACCESS_KEY = "78421343-d4ed-4a10-981f-6194ecfc7122"
SAUCE_URL = f"https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@ondemand.eu-central-1.saucelabs.com/wd/hub"

# Sauce Labs capabilities
sauce_options = {
    "screenResolution": "1920x1080",  # High resolution
    "name": "ClassPass Booking Test",
    "build": "ClassPass_Test_Build"
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

def find_and_select_date(target_date):
    print(f"📌 Looking for target date: {target_date}")

    for _ in range(10):  # Maximum 10 attempts to find the correct date
        try:
            current_date_element = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']")
            current_date_text = current_date_element.text.strip()

            print(f"🔍 Extracted Date from Page: '{current_date_text}' (vs. Target: '{target_date}')")

            if current_date_text == target_date:
                print("✅ Target date found!")
                return  # Exit function if the correct date is displayed

            print("➡ Clicking 'Next Day' button to move forward...")
            next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next day']")
            driver.execute_script("arguments[0].click();", next_button)

            time.sleep(2)  # Allow time for page transition

        except Exception as e:
            print(f"❌ Error finding or clicking date: {e}")
            break  # Stop loop on failure

def find_and_book_class(target_class, target_time):
    print(f"🔍 Searching for class: {target_class} at {target_time}")

    try:
        # Find all class sections
        class_sections = driver.find_elements(By.XPATH, "//section[@data-component='Section']")

        for section in class_sections:
            try:
                # Extract class time
                time_element = section.find_element(By.XPATH, ".//div[@data-qa='ScheduleRow.date']/time/span")
                class_time_text = time_element.text.strip()

                # Extract class name
                name_element = section.find_element(By.XPATH, ".//div[@data-qa='ScheduleRow.classinfo']/h3/strong/a")
                class_name_text = name_element.text.strip()

                print(f"🧐 Checking: {class_name_text} at {class_time_text}")

                if class_name_text == target_class and class_time_text == target_time:
                    print("✅ Found matching class! Attempting to book...")
                    
                    # Click the booking button inside this section
                    book_button = section.find_element(By.XPATH, ".//button[@data-qa='Schedule.cta']")
                    driver.execute_script("arguments[0].click();", book_button)

                    time.sleep(3)
                    print("🎉 Booking Attempted! Moving to final confirmation...")
                    
                    confirm_reservation()
                    return True

            except Exception:
                continue  # Skip if error

        print("❌ Class Not Found")
        return False

    except Exception as e:
        print(f"❌ Error searching for class: {e}")
        return False

def confirm_reservation():
    print("📌 Waiting for confirmation pop-up...")
    time.sleep(2)  # Allow pop-up to load

    try:
        reserve_button = driver.find_element(By.XPATH, "//button[@data-qa='Inquiry.reserve-button']")
        print("✅ 'Reserve' button found! Confirming reservation...")

        driver.execute_script("arguments[0].click();", reserve_button)
        time.sleep(3)  # Allow booking to complete
        print("🎉 Booking Confirmed!")

    except Exception as e:
        print(f"❌ Error confirming reservation: {e}")

if __name__ == "__main__":
    try:
        login()
        navigate_to_studio()
        find_and_select_date("Mon, Feb 3")  # Selecting February 3rd
        find_and_book_class("RIDE45", "8:30 AM")  # Attempt to book
        print("✅ Booking Process Completed")
    except Exception as e:
        print(f"❌ Booking failed: {e}")
    finally:
        driver.quit()
