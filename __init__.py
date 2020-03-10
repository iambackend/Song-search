import os
from multiprocessing.pool import Pool

if __name__ == "__main__":
    if not os.path.exists("cache"):
        os.mkdir("cache")
    pool = Pool()
    pool.