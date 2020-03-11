import asyncio
import multiprocessing
import os
import threading
from multiprocessing.pool import Pool

from app import run_flask
from crawler import init_collection, run_crawler

if __name__ == "__main__":
    if not os.path.exists("cache"):
        os.mkdir("cache")
    full_collection = init_collection(110)
    pool = Pool(3)
    lock = threading.Lock()
    used, unused = full_collection[:55], full_collection[55:110]
    auxiliary_add, auxiliary_drop = [], []
    rebuild = False
    print("what")
    pool.apply_async(run_crawler, [used, unused, auxiliary_add, auxiliary_drop, lock, rebuild])
    print("what")
    run_flask([used, auxiliary_add, auxiliary_drop, lock, rebuild])