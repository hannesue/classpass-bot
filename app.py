from flask import Flask, request, render_template
import os
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
import sys

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

def flush_print(message):
    """ Print with immediate flush """
    print(message)
    sys.stdout.flush()

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

    flush_print("✅ Job scheduled successfully!")

    return "✅ Bot scheduled successfully!"

@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")

    if password != PASSWORD:
        return "<h2 style='color:red; text-align:center;'>❌ Access Denied: Invalid password!</h2>", 403

    try:
        with open(LOG_FILE, "r") as file:
            logs = json.load(file)
    except json.JSONDecodeError:
        logs = []

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Logs</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                width: 100%;
                text-align: center;
            }
            h2 {
                margin-bottom: 20px;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 10px;
                text-align: center;
            }
            th {
                background: #007BFF;
                color: white;
            }
            tr:nth-child(even) {
                background: #f2f2f2;
            }
            .back-button {
                display: inline-block;
                margin-top: 15px;
                padding: 10px 15px;
                background: #007BFF;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: 0.3s;
            }
            .back-button:hover {
                background: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📋 Scheduled Bots Log</h2>
            <table>
                <tr>
                    <th>Class</th>
                    <th>Class Time</th>
                    <th>Scheduler</th>
                    <th>Scheduled At</th>
                </tr>"""

    for log in logs:
        html += f"""
                <tr>
                    <td>{log['class_name']}</td>
                    <td>{log['class_time']}</td>
                    <td>{log['email']}</td>
                    <td>{log['timestamp']}</td>
                </tr>"""

    html += """
            </table>
            <a class="back-button" href="/">⬅️ Back to Scheduler</a>
        </div>
    </body>
    </html>
    """
    return html

def start_bot():
    flush_print("🔄 Background bot is now running...")

    while True:
        try:
            with open(JOB_FILE, "r") as file:
                job = json.load(file)
            flush_print(f"📅 Scheduled job: {job}")

            if not job:
                flush_print("⏳ No job found, checking again in 60 seconds...")
                time.sleep(60)
                continue

            booking_time = datetime.strptime(job["booking_time"], "%Y-%m-%dT%H:%M")
            flush_print(f"⏳ Waiting for booking time: {booking_time} (Current time: {datetime.now()})")

            while datetime.now() < booking_time:
                flush_print(f"⏳ Current time: {datetime.now()} | Waiting for {booking_time}...")
                time.sleep(10)

            flush_print("🚀 Running the bot now!")
            # Add Selenium booking code here

        except Exception as e:
            flush_print(f"❌ Error: {e}")

        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    flush_print("🚀 Bot process started in the background!")
    app.run(host="0.0.0.0", port=5000)
