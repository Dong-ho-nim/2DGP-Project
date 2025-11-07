from pico2d import *

running = True
current_mode = None
frame_time = 0.0

def run(start_mode):
    global current_mode, running
    current_mode = start_mode
    current_mode.enter()

    global frame_time
    running = True
    while running:
        frame_time = get_frame_time()

        events = get_events()
        for e in events:
            current_mode.handle_event(e)

        current_mode.update()
        current_mode.draw()

    current_mode.exit()

def quit():
    global running
    running = False