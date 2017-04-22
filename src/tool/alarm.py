import time

import winsound


def alarm(times=10):
    while times:
        winsound.Beep(400, 1000)
        time.sleep(1)
        times -= 1


def alarm_up():
    winsound.Beep(300, 300)
    winsound.Beep(400, 300)
    winsound.Beep(500, 300)


def alarm_down():
    winsound.Beep(500, 300)
    winsound.Beep(400, 300)
    winsound.Beep(300, 300)