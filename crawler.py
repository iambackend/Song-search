import random
import time

import search_engine as se


def init_collection(size):
    return se.get_collection(size)


def run_crawler(*args):
    cut_collection, uncut_collection, auxiliary_add, auxiliary_drop, lock, rebuild = args
    while True:
        for i in range(10):
            time.sleep(0.1)
            with lock:
                _id = random.choice(list(uncut_collection.keys()))
                auxiliary_add[_id] = uncut_collection[_id]
                _id = random.choice(list(cut_collection.keys()))
                auxiliary_drop[_id] = cut_collection[_id]

        with lock:
            rebuild = True
            for key, item in auxiliary_drop.items():
                if item in cut_collection:
                    uncut_collection[key] = item
                    del cut_collection[key]
            for key, item in auxiliary_add.items():
                if item in uncut_collection:
                    cut_collection[key] = item
                    del uncut_collection[key]
            auxiliary_drop.clear()
            auxiliary_add.clear()
