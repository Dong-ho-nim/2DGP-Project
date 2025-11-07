from pico2d import load_image
import game_framework

class Byakuya:
    def __init__(self, x=800, y=300):
        self.x = x
        self.y = y
        self.frame = 0
        self.state = "Idle"
        self.image = load_image('byakuya.png')  # 투명 배경 PNG 준비

        # 애니메이션 정의 (row 값은 스프라이트 시트에 맞게 조정)
        self.anim_defs = {
            "Idle": {"row": 2, "w": 66, "h": 108, "cols": 8, "fps": 8},
            "WalkRight": {"row": 3, "w": 66, "h": 108, "cols": 8, "fps": 8},
            "WalkLeft": {"row": 3, "w": 66, "h": 108, "cols": 8, "fps": 8},  # 같은 row 사용, draw에서 반전
        }

        self._anim_acc = 0.0

    def set_state(self, state):
        if state in self.anim_defs:
            self.state = state
            self.frame = 0
            self._anim_acc = 0.0

    def update(self):
        anim = self.anim_defs[self.state]
        period = 1.0 / anim["fps"]
        self._anim_acc += getattr(game_framework, 'frame_time', 0.0)
        while self._anim_acc >= period:
            self.frame = (self.frame + 1) % anim["cols"]
            self._anim_acc -= period

        # 이동 처리
        if self.state == "WalkRight":
            self.x += 5
        elif self.state == "WalkLeft":
            self.x -= 5

    def draw(self):
        anim = self.anim_defs[self.state]
        frame_x = self.frame * anim["w"]
        frame_y = anim["row"] * anim["h"]

        if self.state == "WalkLeft":
            # 좌우 반전
            self.image.clip_composite_draw(frame_x, frame_y, anim["w"], anim["h"],
                                           0, 'h', self.x, self.y, anim["w"], anim["h"])
        else:
            # Idle, WalkRight
            self.image.clip_draw(frame_x, frame_y, anim["w"], anim["h"], self.x, self.y)