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
            "MUAY
