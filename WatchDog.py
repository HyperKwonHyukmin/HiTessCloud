import subprocess
import time
import requests
import psutil
import os

FLASK_URL = "http://10.14.42.145:9091/"
CHECK_INTERVAL = 60  # 초
TIMEOUT_SECONDS = 3

def is_server_alive():
    try:
        r = requests.get(FLASK_URL, timeout=TIMEOUT_SECONDS)
        return r.status_code == 200
    except Exception:
        return False

def kill_process(proc):
    try:
        parent = psutil.Process(proc.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"[Error] Failed to kill process: {e}")

def monitor():
    while True:
        os.chdir(r"C:\Users\HHI\KHM\HiTessCloud_Flask")
        print("[Monitor] Starting Flask server...")
        proc = subprocess.Popen(["python", "run.py"])

        while True:
            time.sleep(CHECK_INTERVAL)

            if not is_server_alive():
                print("[Monitor] Flask not responding. Restarting...")
                kill_process(proc)
                break  # while True를 빠져나와 재시작
            else:
                print("[Monitor] Flask is healthy.")

if __name__ == "__main__":
    monitor()
