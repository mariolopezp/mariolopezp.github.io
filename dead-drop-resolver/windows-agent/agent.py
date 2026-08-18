#The main objective of this script is to have the loop running, polling to the RPI
import time
from client import get_task
from dispatcher import select_task

def main():
    print("Windows Agent initiated")
    json_task = None
    while True:
        json_task = get_task()
        select_task(json_task)
        time.sleep(10)


if __name__ == "__main__":
    main()