from pico2d import load_image
import game_framework


class BasePlayer:
    def __init__(self, x, y, sheet_path: str, animations: dict, default_anim: str):
        # animations: { name: {row:int, w:int, h:int, cols:int, fps:int} }
        self.x = x
        self.y = y
        self.image = load_image(sheet_path)
        self.animations = animations
        self.current = default_anim
        self.frame = 0
        self._acc = 0.0
        # 현재 애니메이션 속성 캐시
        self.row = 0
        self.w = 0
        self.h = 0
        self.cols = 1
        self.fps = 1
        self._apply_anim_props()

    def _apply_anim_props(self):
        cfg = self.animations[self.current]
        self.row = cfg.get('row', 0)
        self.w = cfg.get('w', 32)
        self.h = cfg.get('h', 32)
        self.cols = cfg.get('cols', 1)
        self.fps = cfg.get('fps', 6)

    def set_animation(self, name: str):
        if name == self.current or name not in self.animations:
            return
        self.current = name
        self.frame = 0
        self._acc = 0.0
        self._apply_anim_props()

    def update(self):
        period = 1.0 / max(1, self.fps)
        self._acc += getattr(game_framework, 'frame_time', 0.0)
        while self._acc >= period:
            self.frame = (self.frame + 1) % self.cols
            self._acc -= period

    def draw(self):
        left = self.frame * self.w
        bottom = self.image.h - (self.row + 1) * self.h
        if bottom < 0:
            bottom = 0
        self.image.clip_draw(left, bottom, self.w, self.h, self.x, self.y)

    def get_bb(self):
        return self.x - self.w//2, self.y - self.h//2, self.x + self.w//2, self.y + self.h//2

    def handle_collision(self, group, other):
        pass
