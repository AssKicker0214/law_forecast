#encoding=utf-8
import time
###bad
init_time = 0
total_count = 0
def start(total):
    init_time = time.time()
    total_count = total
    return init_time

def peek(done_count):
    current_time = time.time()
    pass_time = current_time - init_time
    return (total_count - done_count)*(pass_time/(done_count+0.0))

def stop():
    end_time = time.time()
    return (end_time-init_time)