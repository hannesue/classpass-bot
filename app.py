from flask import Flask, request, render_template
import os
import json
import time
import multiprocessing
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# File paths
JOB_FILE = "jobs.json"
LOG_FILE = "logs.json"
PASSWORD = "DietCoke"  # Password for logs page

# Ensure log files exist
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump({}, file)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file)

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

    # Save latest job
    with open(JOB_FILE, "w") as file:
        json.dump(job, file)

    # Append job to logs
    with open(LOG_FILE, "r+") as file:
        try:
            logs = json.load(file)
        except json.JSONDecodeError:
            logs = []

        logs.append({
            "class_name": job["class_name"],
            "class_time": job["class_time"],
            "email": job["email"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        file.seek(0)
        json.dump(logs, file)

    print("✅ Job scheduled successfully!")

    return "✅ Bot scheduled successfully!"

def worker():
    """Worker process that continuously checks for scheduled jobs and executes them."""
    print("🚀 Background Worker Started...")

    while True:
        try:
            with open(JOB_FILE, "r") as file:
                job = json.load(file)

            if not job or "booking_time" not in job:
                print("⏳ No valid job found, checking again in 60 seconds...")
                time.sleep(60)
                continue

            booking_time = datetime.strptime(job["booking_time"], "%Y-%m-%dT%H:%M")
            print(f"⏳ Waiting for booking time: {booking_time} (Current time: {datetime.now()})")

            if datetime.now() >= booking_time:
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

                print(f"🎯 Attempting to book class '{job['class_name']}' at '{job['class_time']}'")

                driver.quit()

                open(JOB_FILE, "w").close()  # Clear job after execution
                print("✅ Job completed and cleared.")

        except Exception as e:
            print(f"❌ Error in worker: {e}")

        time.sleep(60)  # Sleep and check again

if __name__ == '__main__':
    # Start worker in a separate process before starting Flask
    bot_process = multiprocessing.Process(target=worker, daemon=True)
    bot_process.start()
    print("🚀 Worker Process Started!")
    
    app.run(host="0.0.0.0", port=10000, debug=True)
