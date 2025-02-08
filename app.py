from flask import Flask, render_template, request, jsonify
import os
import json
import subprocess

app = Flask(__name__)

# File Paths
JOB_FILE = "jobs.json"
PASSWORD = "DietCoke"
GITHUB_PAT = os.getenv("PAT_TOKEN")  # Load from GitHub Secrets
GITHUB_REPO = f"https://x-access-token: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@github.com/hannesue/classpass-bot.git"

# Ensure job file exists
if not os.path.exists(JOB_FILE):
    with open(JOB_FILE, "w") as file:
        json.dump([], file)  # Store jobs as a list

@app.route('/')
def index():
    """ Render the website """
    return render_template("index.html")

@app.route('/schedule', methods=['POST'])
def schedule_bot():
    """ Schedule a new booking and save to jobs.json """
    try:
        job = {
            "email": request.form['email'],
            "password": request.form['password'],
            "studio": request.form['studio'],
            "studio_url": request.form['studio_url'],
            "class_name": request.form['class_name'],
            "date": request.form['date'],
            "time": request.form['time']
        }

        # Read existing jobs.json
        try:
            with open(JOB_FILE, "r") as file:
                jobs = json.load(file)
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
    """ View scheduled bookings """
    try:
        with open(JOB_FILE, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    return jsonify(logs)

@app.route('/delete_single_log', methods=['POST'])
def delete_single_log():
    """ Delete a specific scheduled booking """
    try:
        job_to_delete = request.json  # Get job details from request
        with open(JOB_FILE, "r") as file:
            jobs = json.load(file)

        # Remove job from the list
        jobs = [job for job in jobs if job != job_to_delete]

        # Save the updated jobs.json
        with open(JOB_FILE, "w") as file:
            json.dump(jobs, file, indent=4)

        return jsonify({"message": "✅ Job removed successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_bot', methods=['POST'])
def run_bot_manually():
    """ Manually trigger the booking script """
    try:
        print("🚀 Running booking script manually...")
        subprocess.Popen(["python", "booking.py"])  # ✅ Runs `booking.py`
        return jsonify({"message": "✅ Booking script started!"})
    except Exception as e:
        return jsonify({"error": f"❌ Error running bot: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
