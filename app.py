from flask import Flask, request, render_template
import os
import multiprocessing
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

# Ensure jobs.json exists before reading it
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump({}, file)  # Create an empty JSON file

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
    print("🔄 Background bot is now running...")  # Log when the bot starts

    while True:
        try:
            print("📖 Checking for scheduled jobs...")  # Log when checking for jobs
            
            with open(JOB_FILE, "r") as file:
                job = json.load(file)

            if not job:
                print("⏳ No job found, checking again in 60 seconds...")
                time.sleep(60)
                continue

            booking_time = datetime.strptime(job["booking_time"], "%Y-%m-%dT%H:%M")

            while datetime.now() < booking_time:
                print(f"⏳ Waiting for booking time: {booking_time} (Current time: {datetime.now()})")
                time.sleep(10)

            print("🚀 Running the bot now!")

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get("https://classpass.com/")

            driver.find_element(By.ID, "email").send_keys(job["email"])
            driver.find_element(By.ID, "password").send_keys(job["password"])
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

            time.sleep(5)
            driver.find_element(By.XPATH, f"//input[@placeholder='Search']").send_keys(job["class_name"])
            time.sleep(2)

            print(f"🎯 Attempting to book class '{job['class_name']}' at {job['class_time']}'")

            driver.quit()

            open(JOB_FILE, "w").close()  # Clear job after execution
            print("✅ Job completed and cleared.")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(60)

if __name__ == '__main__':
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
