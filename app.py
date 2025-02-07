from flask import Flask, render_template, request, jsonify
import os
import json
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

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file)

# Ensure job file exists
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump([], file)

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
            "T&S | FULL BODY | ALL IN - 60MIN",
            "T&S | FULL BODY | LOWER BODY FOCUS",
            "T&S | FULL BODY | LOWER BODY FOCUS - 60MIN",
            "HYROX",
            "RIDE45",
            "RIDE60",
            "RHYTHM RIDE",
            "RHYTHM RIDE 60",
            "RHYTHM RIDE - WEEKEND PRINKS",
            "RHYTHM RIDE THEME MAGIC MIKE"
        ]
    },
    "Beatbox": {
        "url": "https://classpass.com/classes/beatbox-fitness-classes--dublin-2",
        "classes": [
            "MUAY THAI FIT Merrion Studio",
            "BOX STRONG - Merrion Studio",
            "KO Leeson Studio",
            "BOX STRONG Leeson Studio",
            "BOX SWEAT - Merrion Studio",
            "HYBRID Merrion Studio",
            "FLATLINE Leeson Studio",
            "FLAT LINE * New Merrion Studio",
            "BOXING PADS - Merrion Studio",
            "BOXING PADS - Leeson Studio",
            "KO Merrion Studio",
            "TECHNICAL BOXING - Merrion Studio",
            "10 ROUNDS - Leeson Studio",
            "PILATES Leeson Studio",
            "FLAT LINE Merrion Studio",
            "10 ROUNDS - Merrion Studio",
            "SPARRING Merrion Studio"
        ]
    }
}

# Generate the next 5 days for the date dropdown
def generate_dates():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%a, %b %d") for i in range(4, 9)]

# Time Slots (6 AM to 8 PM in 5-min intervals)
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
    job = {
        "email": request.form['email'],
        "password": request.form['password'],
        "studio": request.form['studio'],
        "studio_url": STUDIOS[request.form['studio']]['url'],
        "class_name": request.form['class_name'],
        "date": request.form['date'],
        "time": request.form['time']
    }


import subprocess

# Save job to jobs.json
try:
    with open(JOB_FILE, "w") as file:
        json.dump(job, file, indent=4)  # Pretty-print JSON for readability
    print("✅ Job successfully saved to jobs.json!")

    # Commit and push the updated file to GitHub
    subprocess.run(["git", "config", "--global", "user.email", "bot@github.com"], check=True)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions Bot"], check=True)
    subprocess.run(["git", "add", "jobs.json"], check=True)
    subprocess.run(["git", "commit", "-m", "Updated jobs.json with new booking"], check=True)
    subprocess.run(["git", "push"], check=True)

    print("✅ Successfully committed jobs.json to GitHub!")

except Exception as e:
    print(f"❌ Error saving or committing jobs.json: {e}")

    # Store in logs
    with open(LOG_FILE, "r+") as file:
        logs = json.load(file)
        logs.append({
            "user": job["email"],
            "studio": job["studio"],
            "studio_url": job["studio_url"],
            "class_name": job["class_name"],
            "time": f"{job['date']} {job['time']}"
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

@app.route('/delete_log', methods=['POST'])
def delete_log():
    password = request.form.get("password")
    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    with open(LOG_FILE, "w") as file:
        json.dump([], file)

    return jsonify({"message": "✅ Logs cleared successfully!"})

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
            job = json.load(file)

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

        # Select Class Date
        print(f"📅 Searching for date: {job['date']}")
        while True:
            current_date = driver.find_element(By.XPATH, "//div[@data-qa='DateBar.date']").text.strip()
            if current_date == job["date"]:
                print("✅ Correct date found!")
                break
            driver.find_element(By.XPATH, "//button[@aria-label='Next day']").click()
        
        # Find Class and Click Booking Button
        print(f"🔍 Searching for class: {job['class_name']} at {job['time']}")
        class_element = driver.find_element(By.XPATH, f"//h3[contains(text(), '{job['class_name']}')]/../..//time/span[contains(text(), '{job['time']}')]")
        book_button = class_element.find_element(By.XPATH, "./following-sibling::div//button[contains(@aria-label, 'Reserve')]")
        book_button.click()
        print("✅ Class booked successfully!")

        driver.quit()
    except Exception as e:
        print(f"❌ Error during booking: {e}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
