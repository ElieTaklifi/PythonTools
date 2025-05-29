import concurrent.futures
import time
import random

def task(name):
    print(f'Task {name} starting')
    sleep_time = random.randint(1, 5)
    time.sleep(sleep_time)
    print(f'Task {name} complete after {sleep_time} seconds')
    return sleep_time

task_names = ['a', 'b', 'c', 'd', 'e']  # Use letters instead of numbers

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    # Submit tasks with letter names
    future_to_task = {executor.submit(task, name): name for name in task_names}

    for future in concurrent.futures.as_completed(future_to_task):
        task_name = future_to_task[future]
        try:
            result = future.result()
            print(f"Task {task_name} completed successfully with result {result}")
        except Exception as e:
            print(f"Task {task_name} generated an exception: {e}")
