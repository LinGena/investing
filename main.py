from multiprocessing import Process
import os
from db.core import IsDbCreated
from parser.page_content import PageContent
from db.queries import Queries
import time
from config.settings import settings

def first_start():
    os.environ['PYVIRTUALDISPLAY_DISPLAYFD'] = '0'
    task = Queries().get_task()
    PageContent(first_create=True).get(task)

def open_browser_instance(task):
    PageContent().get(task)

def main():
    model = Queries()
    processes: list[Process] = []
    while True:
        task = model.get_task()
        if not task:
            print("No available tasks, waiting for new ones...")
            time.sleep(600)
            continue
        processes = [p for p in processes if p.is_alive()]
        if len(processes) < settings.driver.max_processes:
            p = Process(target=open_browser_instance, args=(task,))
            p.start()
            processes.append(p)
        time.sleep(1)

if __name__ == '__main__':
    IsDbCreated().check()
    first_start()
    main()