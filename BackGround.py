# BackGround.py
from pico2d import load_image, get_canvas_width, get_canvas_height

class BackGround:
    def __init__(self):
        self.sky_image = load_image('Sky.png')
        self.ground_image = load_image('BackGround.png')
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()

    def update(self):
        pass

    def draw(self):
        # Draw sky image, scaling it to fill the canvas
        self.sky_image.clip_draw(
            0, 0, self.sky_image.w, self.sky_image.h,
            self.canvas_width // 2, self.canvas_height // 2,
            self.canvas_width, self.canvas_height
        )
        # Draw ground image, scaling it to fill the canvas
        self.ground_image.clip_draw(
            0, 0, self.ground_image.w, self.ground_image.h,
            self.canvas_width // 2, self.canvas_height // 2,
            self.canvas_width, self.canvas_height
        )