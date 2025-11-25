# Pain.py - 진짜 격투게임 완성본 (1P/2P 완벽 + 커맨드 정확)
from pico2d import load_image, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_a, SDLK_d, SDLK_s, SDLK_w, SDLK_j, SDLK_k, SDLK_l, SDLK_o
from sdl2 import SDLK_KP_1, SDLK_KP_2, SDLK_KP_3, SDLK_KP_4, SDLK_KP_5, SDLK_KP_6, SDLK_KP_7, SDLK_KP_8, SDLK_KP_9
from pico2d import *
import game_framework
import os
from state_machine import StateMachine
import game_world   # 이 줄이 없어서 터졌어요!!!

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'pain', path))

# 이벤트 체크
time_out = lambda e: e[0] == 'TIMEOUT'

# 1P 키
p1_left_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_a
p1_right_down = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_d
p1_down_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_s
p1_up_down    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_w
p1_j_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_j
p1_k_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_k
p1_l_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_l
p1_o_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_o

# 2P 키 (키패드 + 방향키)# 2P 키 (키패드 + 방향키) - 수정된 버전
p2_left_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_LEFT, SDLK_KP_4]
p2_right_down = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_RIGHT, SDLK_KP_6]
p2_down_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_DOWN, SDLK_KP_5]
p2_up_down    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_UP, SDLK_KP_8]
p2_j_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_1, SDLK_KP_7]  # 기술
p2_k_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_2, SDLK_KP_5]  # 2단 점프
p2_l_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_3, SDLK_KP_9]  # 보조 소환

# === 상태 클래스들 (IORI 스타일) ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 5 * game_framework.frame_time * 8) % 5
    def draw(self):
        sx = int(self.frame) * 90
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 90, 90, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 90, 90, 0, 'h', self.p.x, self.p.y, 90, 90)

class Run:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_Run.png')
        self.frame = 0
        if (self.p.player==1 and p1_right_down(e)) or (self.p.player==2 and p2_right_down(e)): self.p.dir = 1
        if (self.p.player==1 and p1_left_down(e))  or (self.p.player==2 and p2_left_down(e)):  self.p.dir = -1
    def exit(self, e): pass
    def do(self):
        self.frame = (self.frame + 10 * game_framework.frame_time * 10) % 10
        self.p.x += self.p.dir * 500 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
    def draw(self):
        sx = int(self.frame) * 90
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 90, 90, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 90, 90, 0, 'h', self.p.x, self.p.y, 90, 90)

class Jump:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_Jump.png')
        self.frame = 0
        self.p.vy = 800
    def exit(self, e): self.p.y = 250
    def do(self):
        self.frame = (self.frame + 6 * game_framework.frame_time * 8) % 6
        self.p.y += self.p.vy * game_framework.frame_time
        self.p.vy -= 2500 * game_framework.frame_time
        if self.p.y <= 250:
            self.p.y = 250
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 90
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 90, 90, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 90, 90, 0, 'h', self.p.x, self.p.y, 90, 90)

class Punch:  # J - 펀치
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Punch.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame += 8 * game_framework.frame_time * 2.2; self.p.state_machine.handle_state_event(('TIMEOUT', None)) if self.frame >= 7.9 else None
    def draw(self):
        sx = int(self.frame) * 130
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 130, 110, self.p.x + 30, self.p.y + 10)
        else:
            self.p.image.clip_composite_draw(sx, 0, 130, 110, 0, 'h', self.p.x - 30, self.p.y + 10, 130, 110)

class Kick:   # K - 점프
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Kick.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame += 10 * game_framework.frame_time * 1.8; self.p.state_machine.handle_state_event(('TIMEOUT', None)) if self.frame >= 9.9 else None
    def draw(self):
        sx = int(self.frame) * 150
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 150, 120, self.p.x + 40, self.p.y - 20)
        else:
            self.p.image.clip_composite_draw(sx, 0, 150, 120, 0, 'h', self.p.x - 40, self.p.y - 20, 150, 120)

class ShinraTensei:  # ↓↘→ + J
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Shinra.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame += 12 * game_framework.frame_time * 1.3; self.p.state_machine.handle_state_event(('TIMEOUT', None)) if self.frame >= 11.9 else None
    def draw(self):
        sx = int(self.frame) * 220
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 220, 220, self.p.x, self.p.y + 100, 660, 660)
        else:
            self.p.image.clip_composite_draw(sx, 0, 220, 220, 0, 'h', self.p.x, self.p.y + 100, 660, 660)

# === 메인 클래스 ===
class Pain:
    def __init__(self, player=1, x=600):
        self.player = player
        self.x, self.y = x, 250
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.vy = 0
        self.image = None
        self.input_buffer = []

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.PUNCH = Punch(self)
        self.KICK = Kick(self)
        self.SHINRA = ShinraTensei(self)

        # 커맨드 체크 함수
        def shinra_cmd(e):
            seq = ''.join(self.input_buffer[-3:])
            return (self.player==1 and p1_j_down(e) and seq in ['236', '263']) or \
                   (self.player==2 and p2_j_down(e) and seq in ['236', '263'])

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player==1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player==2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player==1 and p1_up_down(e)) or (self.player==2 and p2_up_down(e)): self.JUMP,
                lambda e: (self.player==1 and p1_j_down(e)) or (self.player==2 and p2_j_down(e)): self.PUNCH,
                lambda e: (self.player==1 and p1_k_down(e)) or (self.player==2 and p2_k_down(e)): self.KICK,
                shinra_cmd: self.SHINRA,
            },
            self.RUN: {
                lambda e: e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player==1 and p1_up_down(e)) or (self.player==2 and p2_up_down(e)): self.JUMP,
                lambda e: (self.player==1 and p1_j_down(e)) or (self.player==2 and p2_j_down(e)): self.PUNCH,
            },
            self.JUMP: {time_out: self.IDLE},
            self.PUNCH: {time_out: self.IDLE},
            self.KICK: {time_out: self.IDLE},
            self.SHINRA: {time_out: self.IDLE},
        })

    def load_image(self, name):
        self.image = load_resource(name)

    def update(self):
        # 자동으로 상대 바라보기 (game_world.objects 없어도 됨)
        from game_world import objects  # 여기서만 임포트
        for layer in objects:
            for obj in layer:
                if obj != self and isinstance(obj, Pain):
                    self.face_dir = 1 if obj.x > self.x else -1
                    break
            else:
                continue
            break
        self.state_machine.update()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            key = event.key
            if self.player == 1:
                if key == SDLK_s: self.input_buffer.append('2')
                elif key == SDLK_d and self.input_buffer[-1:] == ['2']: self.input_buffer.append('3')
                elif key == SDLK_a and self.input_buffer[-1:] == ['2']: self.input_buffer.append('1')
                elif key == SDLK_d: self.input_buffer.append('6')
                elif key == SDLK_a: self.input_buffer.append('4')
                elif key == SDLK_w: self.input_buffer.append('8')
            else:  # 2P
                if key in [SDLK_DOWN, SDLK_KP_5]:
                    self.input_buffer.append('2')
                elif key in [SDLK_RIGHT, SDLK_KP_6] and self.input_buffer[-1:] == ['2']:
                    self.input_buffer.append('3')
                elif key in [SDLK_LEFT, SDLK_KP_4] and self.input_buffer[-1:] == ['2']:
                    self.input_buffer.append('1')
                elif key in [SDLK_RIGHT, SDLK_KP_6]:
                    self.input_buffer.append('6')
                elif key in [SDLK_LEFT, SDLK_KP_4]:
                    self.input_buffer.append('4')
                elif key in [SDLK_UP, SDLK_KP_8]:
                    self.input_buffer.append('8')
            if len(self.input_buffer) > 12: self.input_buffer = self.input_buffer[-12:]

        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(self.x-60, self.y-100, self.x+60, self.y+20)

    def get_bb(self):
        return self.x-60, self.y-100, self.x+60, self.y+20