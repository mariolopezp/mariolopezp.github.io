import requests
import json
from pathlib import Path
import datetime
import time
import threading
from flask import Flask, jsonify

#The API endpoint:

app = Flask(__name__)

url = "https://mariolopezp.github.io/dead-drop-resolver/tasks.json"

STATE_FILE = Path.home() /"Desktop"/"Hacking"/"dead-drop-resolver"/"state"/"state.json"
LOG_FILE = Path.home() /"Desktop"/"Hacking"/"dead-drop-resolver"/"logs"/"ddr.log"
POLL_INTERVAL = 60

data_lock = threading.Lock()
#Variable that will be accessed by both threads.
shared_state = {
  "data":None,
  "last_updated":None
}

def load_state():
  try:
    with open(STATE_FILE, "r", encoding="utf-8") as file:
      return json.load(file)
  except FileNotFoundError:
    return {"last_task_id": None}


def save_state(state):
  with STATE_FILE.open("w", encoding="utf-8") as file:
    json.dump(state, file, indent=4)


def get_task():
  try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
  except requests.exceptions.Timeout:
    return 0
  except requests.exceptions.TooManyRedirects:
    return 0
  except requests.exceptions.RequestException as e:
    #catastrophic error
    print("Catastrophic error")
    return 0


def record_logs(task, info_string):
  try:
    with open(LOG_FILE, "a", encoding="utf-8") as file:
      ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      if(task==0):
        log_string = f"{ct} INFO {info_string}\n"
        print(log_string, end="")
        file.write(log_string) 
      else:
        task_id = task["task_id"]
        task_type = task["type"]

        log_string = f"{ct} INFO {info_string} task_id: {task_id} task_type: {task_type}\n"

        print(log_string, end="")
        file.write(log_string)

  except Exception as e:
    print(f"Error al guardar el log: {e}")


def check_for_task():
  state = load_state()
  task = get_task()  #task is the field with the whole json response 
  print(task)

  if (task==0):
    print("GitHub poll failed")
    record_logs(task, "POLL FAILED")
  elif "task_id" not in task:
    print("Invalid task: missing task:id")
    return
  elif "type" not in task:
    print("Invalid task: missing task type")
    return
  else:
    task_id = task["task_id"]
    task_type = task["type"]
    last_task_id = state["last_task_id"]

    print(f"Task type: {task_type}")

    if task_id == last_task_id:
      print("No new task")
      record_logs(task, "No new task")
    else:
      print("New task detected")
      print(f"Task type: {task['type']}")
      state["last_task_id"] = task_id
      save_state(state)
      record_logs(task, "Task received")

  return task

def polling_loop():
  while True:
    task_data = check_for_task()
    with data_lock:
      shared_state["data"] = task_data
      shared_state["last_update"] = time.time()
      print("[Poling] JSON updated succesfully")

    time.sleep(POLL_INTERVAL)

def start_flask():
  app.run(host="0.0.0.0", port=8080)

@app.route('/task')
def get_task_server():
  #Return the task.json for the Windows Agent to consume
  with data_lock:
    actual_data = shared_state["data"]
    if actual_data is None:
      return jsonify({"task":"Error"})
  return jsonify(actual_data)


if __name__ == "__main__":
  polling_thread = threading.Thread(target=polling_loop)
  polling_thread.start()

  flask_thread = threading.Thread(target=start_flask)
  flask_thread.start()

  print("Dead Drop Resolver started")

  polling_thread.join()
  flask_thread.join()

