from flask import Flask, request, render_template, jsonify
import os
import json
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Store job data
JOB_FILE = "jobs.json"
LOG_FILE = "logs.json"
PASSWORD = "DietCoke"

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file)

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Studio URLs
STUDIO_URLS = {
    "perpetua": "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt",
    "beatbox": "https://classpass.com/classes/beatbox-fitness-classes--dublin-2"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    job = {
        "email": request.form['email'],
        "password": request.form['password'],
        "studio": request.form['studio'],
        "class_name": request.form['class_name'],
        "class_date": request.form['date'],
        "class_time": request.form['time']
    }

    with open(JOB_FILE, "w") as file:
        json.dump(job, file)

    # Store in logs
    with open(LOG_FILE, "r+") as file:
        logs = json.load(file)
        logs.append({
            "scheduler": job["email"],
            "studio": job["studio"],
            "class_name": job["class_name"],
            "class_date": job["class_date"],
            "class_time": job["class_time"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        file.seek(0)
        json.dump(logs, file)

    print("✅ Job scheduled successfully!")
    return jsonify({"message": "✅ Bot scheduled successfully!"})

@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")
    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    with open(LOG_FILE, "r") as file:
        logs = json.load(file)

    return render_template("logs.html", logs=logs)

def start_bot():
    print("🚀 Running the bot now!")

    try:
        with open(JOB_FILE, "r") as file:
            job = json.load(file)

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(STUDIO_URLS[job["studio"]])
        time.sleep(5)
        
        # Find and select class based on date and time
        class_buttons = driver.find_elements(By.XPATH, f"//div[contains(text(), '{job['class_date']}')]/following::div[contains(text(), '{job['class_name']}')]/following::button")
        
        if class_buttons:
            class_buttons[0].click()
            print(f"🎯 Successfully booked '{job['class_name']}' on {job['class_date']} at {job['class_time']}.")
        else:
            print(f"❌ Class '{job['class_name']}' not found on {job['class_date']} at {job['class_time']}.")

        driver.quit()
        open(JOB_FILE, "w").close()  # Clear job after execution
        print("✅ Job completed and cleared.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
