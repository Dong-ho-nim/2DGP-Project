from pico2d import *
from Player import Byakuya

class Framework:
    def __init__(self, width=800, height=600):
        open_canvas(width, height)
        self.running = True
        self.player = Byakuya()

    def run(self):
        while self.running:
            events = get_events()
            for e in events:
                if e.type == SDL_QUIT:
                    self.running = False

            # 업데이트
            self.player.update()

            # 그리기
            clear_canvas()
            self.player.draw()
            update_canvas()

        close_canvas()