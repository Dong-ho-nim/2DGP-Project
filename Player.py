from pico2d import load_image
import game_framework

class Byakuya:
    def __init__(self, x=800, y=300):
        self.x = x
        self.y = y
        self.frame = 0
        self.state = "Idle"
        self.image = load_image('DS _ DSi - Bleach_ Dark Souls - Characters - Byakuya Kuchiki.png')  # 투명 배경 PNG 준비

        # 애니메이션 정의 (row 값은 스프라이트 시트에 맞게 조정)
        # 맨 위 줄 = row 0, 그 아래 줄 = row 1 ...
        self.anim_defs = {
            "Idle": {"row": 2, "w": 66, "h": 108, "cols": 8, "fps": 8},   # 위에서 두 번째 줄
            "WalkRight": {"row": 5, "w": 66, "h": 108, "cols": 8, "fps": 8},
            "WalkLeft": {"row": 5, "w": 66, "h": 108, "cols": 8, "fps": 8},  # 같은 줄 사용, draw에서 반전
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

        # 이동은 Walk 상태일 때만
        if self.state == "WalkRight":
            self.x += 5
        elif self.state == "WalkLeft":
            self.x -= 5

    def draw(self):
        anim = self.anim_defs[self.state]
        frame_x = self.frame * anim["w"]

        # 위에서 row번째 줄을 계산 (pico2d는 좌하단 기준이므로 변환 필요)
        bottom = (self.image.h) - ((anim["row"] + 1) * anim["h"])
        if bottom < 0:
            bottom = 0

        if self.state == "WalkLeft":
            # 좌우 반전
            self.image.clip_composite_draw(frame_x, bottom, anim["w"], anim["h"],
                                           0, 'h', self.x, self.y, anim["w"], anim["h"])
        else:
            # Idle, WalkRight
            self.image.clip_draw(frame_x, bottom, anim["w"], anim["h"], self.x, self.y)