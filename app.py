from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

app = Flask(__name__)

# Scheduler for running tasks
scheduler = BackgroundScheduler()
scheduler.start()

# Store scheduled jobs in memory (use a database for production)
scheduled_jobs = {}

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML form

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    # Get form data
    email = request.form['email']
    password = request.form['password']
    class_name = request.form['class_name']
    class_time = request.form['class_time']
    booking_time = request.form['booking_time']  # Time to run the bot (from form input)

    try:
        # Convert HTML `datetime-local` format (YYYY-MM-DDTHH:MM) to required format (YYYY-MM-DD HH:MM:SS)
        booking_time = datetime.strptime(booking_time, "%Y-%m-%dT%H:%M")  # Remove 'T' separator
    except ValueError as e:
        return f"❌ Invalid date format! Error: {str(e)}"

    # Schedule the bot
    job_id = f"{email}-{class_name}-{booking_time}"
    if job_id not in scheduled_jobs:
        scheduler.add_job(
            func=run_bot,
            trigger="date",
            run_date=booking_time.strftime("%Y-%m-%d %H:%M:%S"),  # Ensure correct format
            args=[email, password, class_name, class_time],
            id=job_id
        )
        scheduled_jobs[job_id] = True

    return f"✅ Bot scheduled to book '{class_name}' at '{class_time}' on '{booking_time}'!"

def run_bot(email, password, class_name, class_time):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://classpass.com/")

    # Log in to ClassPass
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

    # Wait for the page to load
    time.sleep(5)

    # Search for the class and book it
    driver.find_element(By.XPATH, f"//input[@placeholder='Search']").send_keys(class_name)
    time.sleep(2)

    # Simulate booking the class (replace this with real booking logic)
    print(f"Attempting to book class '{class_name}' at {class_time}")

    driver.quit()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
