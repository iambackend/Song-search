import asyncio
import multiprocessing
import os
import threading
from multiprocessing.pool import ThreadPool

from app import run_flask
from crawler import init_collection, run_crawler

if __name__ == "__main__":
    if not os.path.exists("cache"):
        os.mkdir("cache")
    full_collection = init_collection(110)
    pool = ThreadPool(3)
    lock = threading.Lock()
    used, unused = full_collection[:100], full_collection[100:110]
    auxiliary_add, auxiliary_drop = [], []
    rebuild = False
    crawler_thread = threading.Thread(target=run_crawler, args=(used, unused, auxiliary_add, auxiliary_drop, lock, rebuild))
    crawler_thread.start()
    flask_thread = threading.Thread(target=run_flask, args=(used, auxiliary_add, auxiliary_drop, lock, rebuild))
    flask_thread.start()