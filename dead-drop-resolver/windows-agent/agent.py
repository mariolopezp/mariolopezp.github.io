#The main objective of this script is to have the loop running, polling to the RPI
import time
from client import get_task
from dispatcher import select_task

def main():
    print("Windows Agent initiated")
    while True:
        task_id = int(get_task())
        print(f"Task_id:{task_id}")
        select_task(task_id)
        time.sleep(10)


if __name__ == "__main__":
    main()