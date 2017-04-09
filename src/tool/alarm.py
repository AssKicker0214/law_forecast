import time

import winsound


def alarm(times=10):
    while times:
        winsound.Beep(400, 1000)
        time.sleep(1)
        times -= 1