import random
import time

import search_engine as se


def init_collection(size):
    return se.get_collection(size)


def run_crawler(args):
    cut_collection, uncut_collection, auxiliary_add, auxiliary_drop, lock, rebuild = args
    print(args)
    while True:
        for i in range(10):
            time.sleep(10)
            #unsafe
            auxiliary_add.append(random.choice(uncut_collection))
            auxiliary_drop.append(random.choice(cut_collection))
        # unsafe
        rebuild = True
        for item in auxiliary_drop:
            if item in cut_collection:
                uncut_collection.add(item)
                cut_collection.remove(item)
        for item in auxiliary_add:
            if item not in cut_collection:
                cut_collection.add(item)
                uncut_collection.remove(item)
