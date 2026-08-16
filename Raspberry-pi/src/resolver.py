import requests
import json
from pathlib import Path
import datetime
import time

#The API endpoint:
url = "https://mariolopezp.github.io/dead-drop-resolver/tasks.json"

STATE_FILE = Path.home() /"Desktop"/"Hacking"/"dead-drop-resolver"/"state"/"state.json"
LOG_FILE = Path.home() /"Desktop"/"Hacking"/"dead-drop-resolver"/"logs"/"ddr.log"
POLL_INTERVAL = 60

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


def main():
  print("Dead Drop Resolver started")

  while True:
    check_for_task()
    time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
  main()


