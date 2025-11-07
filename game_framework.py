from pico2d import *
import time

running = True
current_mode = None
frame_time = 0.0
prev_time = 0.0

def run(start_mode):
    global current_mode, running, frame_time, prev_time
    current_mode = start_mode
    current_mode.enter()

    running = True
    prev_time = time.time()

    while running:
        # frame_time 계산
        now = time.time()
        frame_time = now - prev_time
        prev_time = now

        # 이벤트 처리
        events = get_events()
        for e in events:
            current_mode.handle_event(e)

        # 업데이트 & 그리기
        current_mode.update()
        current_mode.draw()

    current_mode.exit()

def quit():
    global running
    running = False