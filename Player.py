from pico2d import load_image, get_time
import game_framework

class Byakuya:
    def __init__(self):
        self.x = 600
        self.y = 150
        self.image = load_image('DS _ DSi - Bleach_ Dark Souls - Characters - Byakuya Kuchiki.png')
        self.anim_defs = {
            "Idle": {"row": 0, "w": 69, "h": 100, "cols": 8, "fps": 6},
        }
        self.current_anim = "Idle"
        self.frame = 0

    def update(self):


    def draw(self):
        self.image.draw(self.anim_defs)