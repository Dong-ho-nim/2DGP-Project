from pico2d import load_image, get_time
import game_framework


class Byakuya:
    def __init__(self, x=800, y=300):
        self.x = x
        self.y = y
        self.frame = 0
        self.dir = 0
        self.wait_time = get_time()
        self.image = load_image('DS _ DSi - Bleach_ Dark Souls - Characters - Byakuya Kuchiki.png')
        # 스프라이트 시트 파라미터(필요시 값만 바꿔서 튜닝)
        self.frame_w = 71
        self.frame_h = 106
        self.frames_per_row = 8
        # "시트의 윗줄" = 0, 그 아래줄 = 1, ...
        self.row_from_top = 2
        self.top_margin = 0  # 시트 최상단 여백이 있으면 픽셀값으로 보정
        # 균일 배치 보정값
        self.left_margin = 0
        self.col_gap = 0
        # 가변 클립(프레임 폭/높이가 제각각인 경우 사용)
        # 각 원소: (left_from_left, top_from_top, width, height)
        self.use_rects = False
        self.top_row_rects = []
        # 애니메이션 속도 제어
        self.anim_fps = 8  # 초당 프레임 수 (필요 시 조정)
        self._anim_acc = 0.0

    # 간단한 튜닝용 setter들
    def set_frame_size(self, w, h):
        self.frame_w, self.frame_h = w, h

    def set_frames_per_row(self, n):
        self.frames_per_row = max(1, int(n))

    def set_row_from_top(self, row, top_margin=0):
        self.row_from_top = max(0, int(row))
        self.top_margin = max(0, int(top_margin))

    def set_uniform_layout(self, left_margin=0, col_gap=0):
        self.left_margin = int(left_margin)
        self.col_gap = int(col_gap)
        self.use_rects = False

    def set_top_row_rects(self, rects):
        """
        rects: [(left_from_left, top_from_top, w, h), ...]  이미지 좌상단 기준
        """
        self.top_row_rects = [(int(l), int(t), int(w), int(h)) for (l, t, w, h) in rects]
        self.frames_per_row = max(1, len(self.top_row_rects))
        self.use_rects = True

    def set_anim_fps(self, fps):
        self.anim_fps = max(1, int(fps))

    def update(self):
        # frame_time 누적으로 프레임 속도 제어
        period = 1.0 / self.anim_fps
        self._anim_acc += getattr(game_framework, 'frame_time', 0.0)
        while self._anim_acc >= period:
            self.frame = (self.frame + 1) % self.frames_per_row
            self._anim_acc -= period

    def draw(self):
        frame = self.frame

        if self.use_rects and self.top_row_rects:
            # 좌상단 기준 rect를 하단 기준으로 변환하여 clip
            l, top, w, h = self.top_row_rects[frame]
            bottom = self.image.h - (top + h)
            if bottom < 0:
                bottom = 0
            self.image.clip_draw(l, bottom, w, h, self.x, self.y)
            return

        # 균일 프레임 계산(좌->우로 진행), 열 간격과 좌측 여백 보정
        fw, fh = self.frame_w, self.frame_h
        left = self.left_margin + frame * (fw + self.col_gap)
        bottom = (self.image.h - self.top_margin) - ((self.row_from_top + 1) * fh)
        if bottom < 0:
            bottom = 0
        self.image.clip_draw(left, bottom, fw, fh, self.x, self.y)
