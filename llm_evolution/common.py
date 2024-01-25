# for xetcache.  Note this gives a lot of too many open file errors.
run_tag = "_2024-01"

import sys


__current_completed = 0
__total = 0

def set_run_total(n):
    __current_completed = 0
    __total = n


def report_task_completed(ch):
    global __current_completed 
    global __total

    __current_completed += 1
            
    sys.stderr.write(ch)
    sys.stderr.flush()

    if __current_completed % 100 == 0: 
        sys.stderr.write(f" {__current_completed} / {__total}\n")
