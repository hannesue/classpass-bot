from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Database setup
DB_FILE = "classpass.db"
PASSWORD = "DietCoke"

# Ensure database exists and create table
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT,
                        password TEXT,
                        class_name TEXT,
                        class_time TEXT,
                        booking_time TEXT,
                        status TEXT DEFAULT 'Pending',
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, class_name, class_time, booking_time, status FROM schedules")
        jobs = cursor.fetchall()
    return render_template('index.html', jobs=jobs)

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    job = (
        request.form['email'],
        request.form['password'],
        request.form['class_name'],
        request.form['class_time'],
        request.form['booking_time'],
        "Pending"
    )

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schedules (email, password, class_name, class_time, booking_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, job)
        conn.commit()

    # Schedule bot execution
    run_time = datetime.strptime(request.form['booking_time'], "%Y-%m-%dT%H:%M")
    scheduler.add_job(start_bot, 'date', run_date=run_time, args=[cursor.lastrowid])

    return jsonify({"message": "✅ Bot scheduled successfully!"})

@app.route('/logs', methods=['GET'])
def view_logs():
    password = request.args.get("password")
    if password != PASSWORD:
        return "❌ Access Denied: Invalid password!", 403

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, class_name, class_time, status, timestamp FROM schedules")
        logs = cursor.fetchall()
    
    return render_template("logs.html", logs=logs)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedules WHERE id = ?", (job_id,))
        conn.commit()
    return jsonify({"message": "✅ Job deleted successfully!"})

def start_bot(job_id):
    print(f"🚀 Running bot for job ID {job_id}")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM schedules WHERE id = ?", (job_id,))
            job = cursor.fetchone()
        
        if not job:
            print("❌ No job found!")
            return

        # Extract details
        email, password, class_name, class_time = job[1], job[2], job[3], job[4]

        # Setup Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://classpass.com/")

        # Login
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        time.sleep(5)

        # Search for the class
        driver.find_element(By.XPATH, "//input[@placeholder='Search']").send_keys(class_name)
        time.sleep(2)

        print(f"🎯 Attempting to book class '{class_name}' at '{class_time}'")

        driver.quit()

        # Update job status
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE schedules SET status = 'Booked' WHERE id = ?", (job_id,))
            conn.commit()
        print("✅ Job completed and updated to 'Booked'.")

    except Exception as e:
        print(f"❌ Error: {e}")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE schedules SET status = 'Failed' WHERE id = ?", (job_id,))
            conn.commit()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
