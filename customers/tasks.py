# customers/tasks.py

from celery import shared_task
import time

@shared_task
def test_task():
    time.sleep(5)
    print("Task completed")
    return "Done"
