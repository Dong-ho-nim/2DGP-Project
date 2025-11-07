# game_framework.py
from pico2d import *

running = True
current_mode = None
frame_time = 0.0

def run(start_mode):
    global current_mode, running, frame_time
    current_mode = start_mode
    current_mode.enter()

    prev_time = get_time()
    frame_time = 0.0

    while running:
        current_time = get_time()
        frame_time = current_time - prev_time
        prev_time = current_time

        events = get_events()
        for e in events:
            current_mode.handle_event(e)

        current_mode.update()
        current_mode.draw()

        # 짧은 딜레이로 CPU 사용량을 줄임
        delay(0.01)

    current_mode.exit()

def quit():
    global running
    running = False