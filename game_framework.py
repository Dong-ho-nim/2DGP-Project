# game_framework.py (이미 좋음, 약간 수정)
from pico2d import *
import time

running = True
current_mode = None
frame_time = 0.0
prev_time = 0.0


# game_framework.py (마지막 부분 수정)
def run(start_mode):
    global current_mode, running, frame_time, prev_time
    current_mode = start_mode
    current_mode.enter()
    running = True
    prev_time = time.time()

    while running:
        now = time.time()
        frame_time = now - prev_time
        prev_time = now

        events = get_events()
        for e in events:
            current_mode.handle_events(e)

        current_mode.update()
        current_mode.draw()

        # delay(0.01) 제거! + ESC 처리
        delay(0.001)  # 아주 짧게d

    current_mode.exit()

def quit():
    global running
    running = False