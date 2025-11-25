import game_framework

class IdleState:
    def enter(self, player):
        cfg = player.anim_defs["Idle"]
        player.fps = cfg.get("fps", 6)  # 느리게: 6fps
        player.row = cfg.get("row", 0)
        player.w = cfg.get("w", 71)
        player.h = cfg.get("h", 106)
        player.cols = cfg.get("cols", 8)

    def exit(self, player):
        pass

    def update(self, player):
        period = 1.0 / max(1, player.fps)
        player._acc += getattr(game_framework, "frame_time", 0.0)
        while player._acc >= period:
            player.frame = (player.frame + 1) % player.cols
            player._acc -= period

    def draw(self, player):
        left = player.frame * player.w
        # pico2d 이미지 원점: 좌하단. row=0은 최상단 한 줄.
        bottom = player.image.h - (player.row + 1) * player.h
        if bottom < 0:
            bottom = 0
        player.image.clip_draw(left, bottom, player.w, player.h, player.x, player.y)

