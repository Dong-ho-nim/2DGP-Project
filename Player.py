from pico2d import load_image, get_time

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
        self.last_time = get_time()

    def update(self):
        anim = self.anim_defs[self.current_anim]
        now = get_time()
        # fps 기준으로 프레임 전환
        if now - self.last_time > 1.0 / anim["fps"]:
            self.frame = (self.frame + 1) % anim["cols"]
            self.last_time = now

    def draw(self):
        anim = self.anim_defs[self.current_anim]
        # 현재 프레임의 x 좌표 계산
        frame_x = self.frame * anim["w"]
        frame_y = anim["row"] * anim["h"]

        # clip_draw(잘라서 그리기)
        self.image.clip_draw(frame_x, frame_y, anim["w"], anim["h"], self.x, self.y)