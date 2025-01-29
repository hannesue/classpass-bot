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
        logs = json.load(file)
        logs.append({
            "class_name": job["class_name"],
            "class_time": job["class_time"],
            "booking_time": job["booking_time"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        file.seek(0)
        json.dump(logs, file)

    print("✅ Job scheduled successfully!")
    return "✅ Bot scheduled successfully!"

@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")

    if password != PASSWORD:
        return "<h2 style='color:red; text-align:center;'>❌ Access Denied: Invalid password!</h2>", 403

    with open(LOG_FILE, "r") as file:
        logs = json.load(file)

    # Modern HTML Template for Logs
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
                    <th>Booking Time</th>
                    <th>Scheduled At</th>
                </tr>"""

    for log in logs:
        html += f"""
                <tr>
                    <td>{log['class_name']}</td>
                    <td>{log['class_time']}</td>
                    <td>{log['booking_time']}</td>
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
    print("🔄 Background bot is now running...")

    while True:
        try:
            with open(JOB_FILE, "r") as file:
                job = json.load(file)

            if not job:
                print("⏳ No job found, checking again in 60 seconds...")
                time.sleep(60)
                continue

            try:
                booking_time = datetime.strptime(job["booking_time"], "%Y-%m-%dT%H:%M")
                print(f"⏳ Waiting for booking time: {booking_time} (Current time: {datetime.now()})")
            except Exception as e:
                print(f"❌ Error parsing booking time: {e}")
                time.sleep(60)
                continue

            while datetime.now() < booking_time:
                print(f"⏳ Current time: {datetime.now()} | Waiting for {booking_time}...")
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

            print(f"🎯 Attempting to book class '{job['class_name']}' at '{job['class_time']}'")

            driver.quit()

            open(JOB_FILE, "w").close()  # Clear job after execution
            print("✅ Job completed and cleared.")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(60)

if __name__ == '__main__':
    bot_process = multiprocessing.Process(target=start_bot)
    bot_process.daemon = True  
    bot_process.start()  
    print("🚀 Bot process started in the background!")
    app.run(host="0.0.0.0", port=5000, debug=True)
