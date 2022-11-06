import time

next_queue = {}

# run_after(func, t): func 함수를 t초후에 실행하게 해줌
def run_after(func, t):
    now_time = time.time() + t

    while now_time in next_queue:
        now_time -= 0.000001

    next_queue[now_time] = func

OSONGSTUDIO_VERSION = '1.0X'
MUSIC_DIR = 'Music'