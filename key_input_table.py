# key_input_table.py  ← 완성본! 바로 복사해서 사용하세요
# Naruto vs Bleach 완전한 키 입력 테이블 + 입력 버퍼 시스템 (P1 / P2 완벽 분리)

from collections import deque
import game_framework
# key_input_table.py 맨 위에 이 줄 추가! (기존 import 아래에)
from sdl2 import *

# ──────────────────────────────────────
# 1. 키 코드 정의 (P1 / P2 완전 구분)
# ──────────────────────────────────────
KEY_MAP = {
    # ── Player 1 (왼쪽 플레이어) ─────────────────────
    'P1': {
        'LEFT':  ord('a'),    # ←
        'RIGHT': ord('d'),    # →
        'DOWN':  ord('s'),    # ↓
        'UP':    ord('w'),    # ↑
        'LP':    ord('j'),    # 약펀치
        'MP':    ord('k'),    # 중펀치
        'HP':    ord('l'),    # 강펀치
        'LK':    ord('u'),    # 약킥
        'MK':    ord('i'),    # 중킥
        'HK':    ord('o'),    # 강킥
    },
    # ── Player 2 (오른쪽 플레이어) ─────────────────────
    'P2': {
        'LEFT':  SDLK_LEFT,
        'RIGHT': SDLK_RIGHT,
        'DOWN':  SDLK_DOWN,
        'UP':    SDLK_UP,
        'LP':    SDLK_KP_4,
        'MP':    SDLK_KP_5,
        'HP':    SDLK_KP_6,
        'LK':    SDLK_KP_1,
        'MK':    SDLK_KP_2,
        'HK':    SDLK_KP_3,
    }
}

# ──────────────────────────────────────
# 2. 방향키 기호 (입력 버퍼에서 쓰기 쉽게)
# ──────────────────────────────────────
DIR_SYMBOL = {
    KEY_MAP['P1']['LEFT']:  '4', KEY_MAP['P1']['RIGHT']: '6',
    KEY_MAP['P1']['DOWN']:  '2', KEY_MAP['P1']['UP']:    '8',
    KEY_MAP['P2']['LEFT']:  '4', KEY_MAP['P2']['RIGHT']: '6',
    KEY_MAP['P2']['DOWN']:  '2', KEY_MAP['P2']['UP']:    '8',
}

# ──────────────────────────────────────
# 3. 입력 버퍼 클래스 (격투게임의 심장!)
# ──────────────────────────────────────
class InputBuffer:
    def __init__(self, player='P1', buffer_time=0.3, max_len=15):
        self.player = player
        self.buffer = deque(maxlen=max_len)      # 입력 기록
        self.times  = deque(maxlen=max_len)      # 시간 기록
        self.buffer_time = buffer_time           # 0.3초 내 입력만 인정

    def add(self, key):
        now = game_framework.get_time()
        # 오래된 입력 제거
        while self.times and now - self.times[0] > self.buffer_time:
            self.buffer.popleft()
            self.times.popleft()

        symbol = DIR_SYMBOL.get(key, 'X')  # 방향키면 4,6,2,8 / 공격이면 X
        self.buffer.append(symbol)
        self.times.append(now)

    def check(self, pattern):
        """패턴 예: '236' + 'P'  → ↓↘→ + 펀치"""
        if len(self.buffer) < len(pattern):
            return False
        return ''.join(list(self.buffer)[-len(pattern):]) == pattern

    def clear(self):
        self.buffer.clear()
        self.times.clear()

    def __str__(self):
        return ''.join(self.buffer)

# ──────────────────────────────────────
# 4. 전역 입력 매니저 (모든 캐릭터가 공용으로 사용)
# ──────────────────────────────────────
class GlobalInput:
    def __init__(self):
        self.p1_buffer = InputBuffer('P1')
        self.p2_buffer = InputBuffer('P2')
        self.p1_keys = {k: False for k in KEY_MAP['P1'].values()}
        self.p2_keys = {k: False for k in KEY_MAP['P2'].values()}

    def handle_event(self, event):
        # 안전장치: SDL 키 이벤트만 처리
        from sdl2 import SDL_KEYDOWN, SDL_KEYUP
        if not hasattr(event, 'type') or event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        # 키코드 추출을 안전하게 시도
        key = None
        try:
            key = event.key.keysym.sym
        except Exception:
            # event 구조가 다르면 무시
            return

        # 키 눌림 여부 판단 (repeat이 0일 때만 True로 간주)
        repeat = getattr(event.key, 'repeat', 0)
        down = (event.type == SDL_KEYDOWN and not repeat)

        # P1 처리
        if key in self.p1_keys:
            self.p1_keys[key] = down
            if down:
                self.p1_buffer.add(key)

        # P2 처리
        if key in self.p2_keys:
            self.p2_keys[key] = down
            if down:
                self.p2_buffer.add(key)

# 전역 인스턴스 (어디서든 import 해서 쓰세요!)
input_manager = GlobalInput()

# ──────────────────────────────────────
# 5. 사용 예시 (pain.py 안에서)
# ──────────────────────────────────────
"""
# pain.py 안에서 이렇게 쓰면 됩니다!

def update(self):
    # 대시 (66 or 44)
    if input_manager.p1_check('66'):
        self.dash_forward()
    if input_manager.p1_check('44'):
        self.dash_backward()

    # 신라천정 ↓↘→ + 강펀치
    if input_manager.p1_check('236') and input_manager.p1_pressed('HP'):
        self.shinra_tensei()
        input_manager.p1_buffer.clear()

    # 점프
    if input_manager.p1_pressed('UP'):
        self.jump()
"""