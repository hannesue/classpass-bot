from flask import Flask, render_template, request, jsonify
import os
import json
import subprocess
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# File Paths
JOB_FILE = "jobs.json"
LOG_FILE = "logs.json"
PASSWORD = "DietCoke"
GITHUB_PAT = os.getenv("PAT_TOKEN")  # Load from GitHub Secrets
GITHUB_REPO = f"https://x-access-token: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@github.com/hannesue/classpass-bot.git"

# Ensure job & log files exist
for file_path in [JOB_FILE, LOG_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump([], file)  # Store jobs/logs as lists

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Studio and Class Data
STUDIOS = {
    "Perpetua Fitness": {
        "url": "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt",
        "classes": [
            "T&S | FULL BODY | ALL IN",
            "T&S | GLUTES & ABS",
            "T&S | FULL BODY | INTENSITY",
            "T&S | CHEST, ARMS & ABS",
            "T&S | FULL BODY | STRENGTH",
            "HYROX",
            "RIDE45",
            "RIDE60",
            "RHYTHM RIDE",
        ]
    },
    "Beatbox": {
        "url": "https://classpass.com/classes/beatbox-fitness-classes--dublin-2",
        "classes": [
            "MUAY THAI FIT Merrion Studio",
            "BOX STRONG - Merrion Studio",
            "KO Leeson Studio",
            "BOX SWEAT - Merrion Studio",
            "HYBRID Merrion Studio",
            "FLATLINE Leeson Studio",
        ]
    }
}

# Generate the next 5 days for the date dropdown
def generate_dates():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%a, %b %d") for i in range(4, 9)]

# Generate time slots (6 AM to 8 PM in 5-min intervals)
def generate_time_slots():
    times = []
    for hour in range(6, 21):  # 6 AM to 8 PM
        for minute in range(0, 60, 5):
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            times.append(f"{display_hour}:{minute:02d} {am_pm}")
    return times

# 🔹 WEB UI ROUTE
@app.route('/')
def index():
    return render_template("index.html", studios=STUDIOS, dates=generate_dates(), times=generate_time_slots())

# 🔹 SCHEDULE A JOB (FIXED!)
@app.route('/schedule', methods=['POST'])
def schedule_bot():
    try:
        job = {
            "email": request.form.get('email', "").strip(),
            "password": request.form.get('password', "").strip(),
            "studio": request.form.get('studio', "").strip(),
            "studio_url": STUDIOS.get(request.form.get('studio', ""), {}).get('url', ""),
            "class_name": request.form.get('class_name', "").strip(),
            "date": request.form.get('date', "").strip(),
            "time": request.form.get('time', "").strip()
        }

        # Ensure no missing fields
        if not all(job.values()):
            return jsonify({"error": "❌ Missing required fields!"}), 400

        # Read existing jobs.json data
        try:
            with open(JOB_FILE, "r") as file:
                jobs = json.load(file)
                if not isinstance(jobs, list):
                    jobs = []
        except (FileNotFoundError, json.JSONDecodeError):
            jobs = []

        # Add new job
        jobs.append(job)

        # Save updated jobs.json
        with open(JOB_FILE, "w") as file:
            json.dump(jobs, file, indent=4)
        print("✅ Job successfully saved to jobs.json!")

        return jsonify({"message": "✅ Bot scheduled successfully!"})

    except Exception as e:
        print(f"❌ Error in /schedule: {e}")
        return jsonify({"error": str(e)}), 500

# 🔹 VIEW LOGS
@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")
    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    try:
        with open(JOB_FILE, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    return render_template("logs.html", logs=logs)

# 🔹 DELETE SINGLE JOB
@app.route('/delete_single_log', methods=['POST'])
def delete_single_log():
    password = request.form.get("password")
    index = int(request.form.get("index", "-1"))

    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    with open(JOB_FILE, "r") as file:
        logs = json.load(file)

    if 0 <= index < len(logs):
        logs.pop(index)

        with open(JOB_FILE, "w") as file:
            json.dump(logs, file, indent=4)

        return jsonify({"message": "✅ Log entry deleted successfully!"})

    return jsonify({"error": "❌ Invalid log entry index!"}), 400

# 🔹 MANUAL BOT EXECUTION
@app.route('/run_bot', methods=['POST'])
def run_bot_manually():
    try:
        print("🚀 Running bot manually...")
        start_bot()
        return jsonify({"message": "✅ Bot executed successfully!"})
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return jsonify({"error": str(e)}), 500

# 🔹 FUNCTION TO RUN BOOKING BOT (RESTORED!)
def start_bot():
    try:
        with open(JOB_FILE, "r") as file:
            jobs = json.load(file)

        for job in jobs:
            print(f"🚀 Starting bot for user {job['email']}")

            # Set up Selenium WebDriver
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Open ClassPass login page
            driver.get("https://classpass.com/login")

            # Login
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(job["email"])
            driver.find_element(By.ID, "password").send_keys(job["password"])
            driver.find_element(By.ID, "password").submit()
            print("✅ Logged in successfully!")

            # Open Studio Page
            driver.get(job["studio_url"])
            print(f"🚀 Navigated to studio: {job['studio_url']}")

            driver.quit()

    except Exception as e:
        print(f"❌ Error during booking: {e}")

# 🔹 RUN FLASK APP
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
