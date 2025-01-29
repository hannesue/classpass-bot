from flask import Flask, request, render_template
import threading
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Store the job in a file so it persists
JOB_FILE = "jobs.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    job = {
        "email": request.form['email'],
        "password": request.form['password'],
        "class_name": request.form['class_name'],
        "class_time": request.form['class_time'],
        "booking_time": request.form['booking_time']
    }

    with open(JOB_FILE, "w") as file:
        json.dump(job, file)

    return "✅ Bot scheduled successfully!"

def run_bot():
    while True:
        try:
            with open(JOB_FILE, "r") as file:
                job = json.load(file)

            if not job:
                time.sleep(60)
                continue

            booking_time = datetime.strptime(job["booking_time"], "%Y-%m-%dT%H:%M")
            
            # Wait until it's time to book
            while datetime.now() < booking_time:
                time.sleep(10)

            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

            # Launch WebDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get("https://classpass.com/")

            # Log in to ClassPass
            driver.find_element(By.ID, "email").send_keys(job["email"])
            driver.find_element(By.ID, "password").send_keys(job["password"])
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

            # Wait for the page to load
            time.sleep(5)

            # Search for the class and book it
            driver.find_element(By.XPATH, f"//input[@placeholder='Search']").send_keys(job["class_name"])
            time.sleep(2)

            print(f"Attempting to book class '{job['class_name']}' at {job['class_time']}")

            driver.quit()

            # Clear the job after execution
            open(JOB_FILE, "w").close()

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(60)

# Start bot in background
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
