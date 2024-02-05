cache_dir = "./cache"

import pickle
import hashlib
from os.path import exists, join
import os

version_string=b"VERSION=1:"


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
            data = open(path, "rb").read()
            if data[:len(version_string)] == version_string:
                (_key, output) = pickle.loads(data[len(version_string):])
                return output
            else:
                return pickle.loads(data)
        else:
            return None
    except:
        raise

def save(key, value): 
    path = cache_file(key)
    s = version_string + pickle.dumps((key, value), protocol=-1)
    open(path, "wb").write(s)



