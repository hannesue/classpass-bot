from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

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

# Studio Data
STUDIOS = {
    "Perpetua Fitness": {
        "url": "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt",
        "classes": [
            "T&S | FULL BODY | ALL IN", "T&S | GLUTES & ABS", "T&S | FULL BODY | INTENSITY", "RIDE45", "RHYTHM RIDE"
        ]
    },
    "Beatbox": {
        "url": "https://classpass.com/classes/beatbox-fitness-classes--dublin-2",
        "classes": [
            "MUAY THAI FIT Merrion Studio", "BOX STRONG - Merrion Studio", "KO Leeson Studio", "BOX STRONG Leeson Studio"
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
    for hour in range(6, 21):
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
        print("📥 Incoming Form Data:", request.form)

        studio = request.form['studio']
        studio_url = STUDIOS.get(studio, {}).get("url", "")

        job = {
            "email": request.form['email'],
            "password": request.form['password'],
            "studio": studio,
            "studio_url": studio_url,
            "class_name": request.form['class_name'],
            "date": request.form['date'],
            "time": request.form['time']
        }

        # Save job
        with open(JOB_FILE, "w") as file:
            json.dump(job, file)

        # Store in logs
        with open(LOG_FILE, "r+") as file:
            logs = json.load(file)
            logs.append({
                "user": job["email"],
                "studio": job["studio"],
                "studio_url": job["studio_url"],
                "class_name": job["class_name"],
                "time": f"{job['date']} {job['time']}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            file.seek(0)
            json.dump(logs, file)

        print("✅ Job scheduled successfully!")
        return jsonify({"message": "✅ Bot scheduled successfully!"})

    except Exception as e:
        print(f"❌ Error in /schedule: {e}")
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
