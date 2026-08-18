#This python script has the mission to launch the request to the Raspberry Pi which acts as the resolver.
#The RPI has previously stored the instructions/tasks from the dead-drop, which is the GitHub Page.
import requests

def get_task():
    print("Getting the task from the Raspberry Pi")
    try:
        response = requests.get("http://192.168.1.147:8080/task", timeout=10)
        response.raise_for_status()
        task_data= response.json()
        task_id = task_data.get("task_id")
    except requests.exceptions.RequestException:
        #Generic failure
        task = {"task":"Error"}    
        task_id = "000"
    return task_id