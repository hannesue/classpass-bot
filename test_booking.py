from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    """Setup the Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for GitHub Actions
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login_to_classpass(driver, email, password):
    """Logs into ClassPass."""
    driver.get("https://classpass.com/")
    print("🚀 Navigating to ClassPass Login Page")
    
    try:
        # Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Log in')]"))
        )
        login_button.click()

        # Enter email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys(email)

        # Enter password
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        print("✅ Logged in successfully")
        time.sleep(5)  # Wait for login to complete

    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.quit()
        return False
    
    return True

def select_date(driver, target_date):
    """Navigates to the selected date."""
    try:
        # Wait for the date element to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Select date')]"))
        )

        # Get current date on the page
        current_date_element = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Select date')]")
        current_date = current_date_element.text.strip()

        print(f"📆 Current Date on Page: {current_date} | Target Date: {target_date}")

        # Click forward or backward until the correct date appears
        while current_date != target_date:
            if target_date > current_date:
                next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next day']")
                next_button.click()
            else:
                prev_button = driver.find_element(By.XPATH, "//button[@aria-label='Previous day']")
                prev_button.click()

            # Wait for page update
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, "//button[contains(@aria-label, 'Select date')]"), target_date)
            )

            current_date = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Select date')]").text.strip()

        print("✅ Date Selected Successfully!")

    except Exception as e:
        print(f"❌ Error selecting date: {e}")

def book_class(driver, class_name, class_time):
    """Finds and books the class."""
    try:
        # Look for the class with the correct name and time
        class_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{class_time}')]/following-sibling::div[contains(text(), '{class_name}')]"))
        )

        # Find the corresponding booking button
        booking_button = class_element.find_element(By.XPATH, "./following-sibling::div//button[contains(text(), 'credits')]")
        
        # Click booking button
        booking_button.click()

        print(f"✅ Successfully booked {class_name} at {class_time}!")

    except Exception as e:
        print(f"❌ Booking failed: {e}")

def main():
    """Main bot logic."""
    email = "your-email@example.com"
    password = "your-password"
    studio_url = "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt"
    class_name = "RIDE45"
    class_time = "7:15 AM"
    target_date = "Sun, Feb 2"  # Format: "Thu, Jan 30"

    driver = setup_driver()
    
    if not login_to_classpass(driver, email, password):
        return  # Exit if login fails

    print(f"🚀 Opening Studio: {studio_url}")
    driver.get(studio_url)
    
    select_date(driver, target_date)
    book_class(driver, class_name, class_time)

    driver.quit()
    print("✅ Test Completed")

if __name__ == "__main__":
    main()
