cache_dir = "./cache"

import pickle
import hashlib
from os.path import exists, join
import os


def cache_file(key):
    key_p = pickle.dumps(key, protocol=-1)
    key_s = hashlib.sha256(key_p).hexdigest() + ".pkl"
    subdir_key = key_s[:2]
    subdir = join(cache_dir, subdir_key)
    if not exists(subdir):
        os.makedirs(subdir)

    return  join(subdir, key_s)


# Simple persistant caching that can be checked in easily.
def load(key): 
    try:
        path = cache_file(key)
        if exists(path):
            return pickle.load(open(path, "rb"))
        else:
            return None
    except:
        return None

def save(key, value): 
    path = cache_file(key)
    pickle.dump(value, open(path, "wb"), protocol=-1)



