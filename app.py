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
GITHUB_REPO = f"https://x-access-token:{GITHUB_PAT}@github.com/hannesue/classpass-bot.git"

# Ensure job file exists
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump([], file)  # Store jobs as a list

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

@app.route('/')
def index():
    return render_template("index.html", studios=STUDIOS, dates=generate_dates(), times=generate_time_slots())

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    try:
        job = {
            "email": request.form['email'],
            "password": request.form['password'],
            "studio": request.form['studio'],
            "studio_url": STUDIOS[request.form['studio']]['url'],
            "class_name": request.form['class_name'],
            "date": request.form['date'],
            "time": request.form['time']
        }

        # Read existing jobs.json data
        try:
            with open(JOB_FILE, "r") as file:
                jobs = json.load(file)
                if not isinstance(jobs, list):
                    jobs = []  # Ensure jobs.json is a list
        except (FileNotFoundError, json.JSONDecodeError):
            jobs = []

        # Add new job
        jobs.append(job)

        # Save updated jobs.json
        with open(JOB_FILE, "w") as file:
            json.dump(jobs, file, indent=4)
        print("✅ Job successfully saved to jobs.json!")

        # Commit & push the updated file to GitHub
        subprocess.run(["git", "config", "--global", "user.email", "bot@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions Bot"], check=True)
        subprocess.run(["git", "add", "jobs.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Updated jobs.json with new booking"], check=True)
        subprocess.run(["git", "push", GITHUB_REPO], check=True)

        print("✅ Successfully committed jobs.json to GitHub!")

        return jsonify({"message": "✅ Bot scheduled successfully!"})

    except Exception as e:
        print(f"❌ Error in /schedule: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")
    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    try:
        with open(JOB_FILE, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []  # If file doesn't exist or is corrupted, show empty logs

    return render_template("logs.html", logs=logs)

@app.route('/delete_single_log', methods=['POST'])
def delete_single_log():
    password = request.form.get("password")
    index = int(request.form.get("index"))  # Get the index of the log entry

    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    # Read logs
    with open(JOB_FILE, "r") as file:
        logs = json.load(file)

    if 0 <= index < len(logs):  # Ensure valid index
        logs.pop(index)  # Remove entry

        # Write updated logs back
        with open(JOB_FILE, "w") as file:
            json.dump(logs, file, indent=4)

        return jsonify({"message": "✅ Log entry deleted successfully!"})

    return jsonify({"error": "❌ Invalid log entry index!"}), 400

@app.route('/run_bot', methods=['POST'])
def run_bot_manually():
    try:
        print("🚀 Running bot manually...")
        start_bot()
        return jsonify({"message": "✅ Bot executed successfully!"})
    except Exception as e:
        print(f"❌ Error running bot: {e}")  # Print error to logs
        return jsonify({"error": f"❌ Error running bot: {str(e)}"}), 500

# Function to start the bot
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
