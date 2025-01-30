from flask import Flask, render_template, request, jsonify
import os
import json
import subprocess
from datetime import datetime, timedelta

app = Flask(__name__)

# File Paths
JOB_FILE = "jobs.json"
LOG_FILE = "logs.json"
PASSWORD = "DietCoke"

# Ensure job & log files exist
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump([], file)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file)

# Studio and Class Data
STUDIOS = {
    "Perpetua Fitness": {
        "url": "https://classpass.com/classes/perpetua-fitness--windmill-lane-dublin-lrpt",
        "classes": [
            "T&S | FULL BODY | ALL IN",
            "T&S | GLUTES & ABS",
            "T&S | FULL BODY | INTENSITY",
            "T&S | CHEST, ARMS & ABS",
            "HYROX",
            "RIDE45",
            "RIDE60",
            "RHYTHM RIDE"
        ]
    },
    "Beatbox": {
        "url": "https://classpass.com/classes/beatbox-fitness-classes--dublin-2",
        "classes": [
            "MUAY THAI FIT Merrion Studio",
            "BOX STRONG - Merrion Studio",
            "KO Leeson Studio",
            "BOX SWEAT - Merrion Studio"
        ]
    }
}

# Generate available dates (next 5 days)
def generate_dates():
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%a, %b %d") for i in range(4, 9)]

# Generate time slots from 6AM to 8PM in 5-min intervals
def generate_time_slots():
    return [f"{hour}:{minute:02d} {'AM' if hour < 12 else 'PM'}" for hour in range(6, 21) for minute in range(0, 60, 5)]

@app.route('/')
def index():
    return render_template("index.html", studios=STUDIOS, dates=generate_dates(), times=generate_time_slots())

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    job = {
        "email": request.form['email'],
        "password": request.form['password'],
        "studio": request.form['studio'],
        "class_name": request.form['class_name'],
        "date": request.form['date'],
        "time": request.form['time']
    }

    # Store the booking in jobs.json
    with open(JOB_FILE, "w") as file:
        json.dump([job], file)  # Only one job at a time

    # Append booking to logs
    with open(LOG_FILE, "r+") as file:
        logs = json.load(file)
        logs.append({
            "email": job["email"],
            "studio": job["studio"],
            "class_name": job["class_name"],
            "date": job["date"],
            "time": job["time"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        file.seek(0)
        json.dump(logs, file)

    print("✅ Job scheduled successfully!")
    return jsonify({"message": "✅ Bot scheduled successfully!"})

@app.route('/logs', methods=['GET'])
def view_logs():
    with open(LOG_FILE, "r") as file:
        logs = json.load(file)
    return render_template("logs.html", logs=logs)

@app.route('/delete_log', methods=['POST'])
def delete_log():
    with open(LOG_FILE, "w") as file:
        json.dump([], file)
    return jsonify({"message": "✅ Logs cleared successfully!"})

@app.route('/run_booking', methods=['POST'])
def run_booking():
    try:
        # Run test_booking.py manually
        result = subprocess.run(["python", "test_booking.py"], capture_output=True, text=True)
        print(result.stdout)  # Print execution logs

        return jsonify({"message": "✅ Booking bot executed manually!"})
    except Exception as e:
        return jsonify({"error": f"❌ Error: {e}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
