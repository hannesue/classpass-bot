import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Test Credentials (replace with real ones when needed)
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

# Test Booking Details
STUDIO_URL = "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt"
CLASS_NAME = "RIDE45"
CLASS_TIME = "7:15 AM"
TARGET_DATE = "Fri, Feb 2"  # Change dynamically based on your test case

# Initialize WebDriver
def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Function to log in to ClassPass
def login(driver):
    try:
        print("🚀 Navigating to ClassPass Login Page")
        driver.get("https://classpass.com/")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "password").submit()

        print("✅ Logged in successfully")
        time.sleep(5)  # Allow time for login redirect
    except Exception as e:
        print(f"❌ Login Failed: {e}")

# Function to select the correct date
def select_date(driver, target_date):
    try:
        print("📌 Checking available dates on the page...")

        # Find all available date elements
        date_elements = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Select date')]")

        # Print the dates found
        for el in date_elements:
            print(f"📅 Found Date on Page: {el.text.strip()}")

        # Check if the correct date is already selected
        current_date_element = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Select date')]")
        current_date = current_date_element.text.strip()

        print(f"📆 Current Date on Page: {current_date} | Target Date: {target_date}")

        if not current_date:
            print("❌ ERROR: No date found on the page. The page structure may have changed.")
            return False

        # Click forward or backward until the correct date appears
        while current_date != target_date:
            if target_date > current_date:
                print("➡ Clicking next day...")
                next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next day']")
                next_button.click()
            else:
                print("⬅ Clicking previous day...")
                prev_button = driver.find_element(By.XPATH, "//button[@aria-label='Previous day']")
                prev_button.click()

            # Wait for page update
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, "//button[contains(@aria-label, 'Select date')]"), target_date)
            )

            current_date = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Select date')]").text.strip()

        print("✅ Date Selected Successfully!")
        return True

    except Exception as e:
        print(f"❌ Error selecting date: {e}")
        return False

# Function to book the class
def book_class(driver, class_name, class_time):
    try:
        print(f"🔍 Searching for class: {class_name} at {class_time}")

        # Find all class listings
        class_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'credits')]")

        # Print all classes found
        for el in class_elements:
            print(f"📌 Found Class: {el.text.strip()}")

        # Look for the class with the correct name and time
        class_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{class_time}')]/following-sibling::div[contains(text(), '{class_name}')]"))
        )

        # Find the corresponding booking button
        booking_button = class_element.find_element(By.XPATH, "./following-sibling::div//button[contains(text(), 'credits')]")

        # Click booking button
        booking_button.click()

        print(f"✅ Successfully booked {class_name} at {class_time}!")
        return True

    except Exception as e:
        print(f"❌ Booking failed: {e}")
        return False

# Main execution
def main():
    driver = start_driver()
    login(driver)

    print(f"🚀 Opening Studio: {STUDIO_URL}")
    driver.get(STUDIO_URL)
    time.sleep(5)  # Allow page to load

    if select_date(driver, TARGET_DATE):
        book_class(driver, CLASS_NAME, CLASS_TIME)

    print("✅ Test Completed")
    driver.quit()

if __name__ == "__main__":
    main()
