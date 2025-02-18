from flask import Flask, request, abort
import threading
import time
from dotenv import load_dotenv
import psutil, os
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

try:
    load_dotenv()
except Exception as e:
    print(f"Error loading .env file: {e}")

app = Flask(__name__)

# Prometheus Metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')

def monitor_cpu_usage():
    while True:
        try:
            usage = psutil.cpu_percent()
            cpu_usage.set(usage)
            print(f"CPU Usage Updated: {usage}%")
        except Exception as e:
            print(f"Error in monitoring thread: {e}")
            time.sleep(5)  

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask CPU Metrics App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                text-align: center;
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #007BFF;
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 2rem;
            }
            .metrics-link {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background-color: #007BFF;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }
            .metrics-link:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Flask CPU Metrics App</h1>
            <p>Welcome to the Flask CPU Metrics App! This app monitors CPU usage and exposes metrics for Prometheus.</p>
            <a href="/metrics" class="metrics-link">View Metrics</a>
        </div>
    </body>
    </html>
    """

@app.route('/metrics')
def metrics():
    try:
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        return str(e), 500

def main():
    monitor_thread = threading.Thread(target=monitor_cpu_usage, daemon=True)
    monitor_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
