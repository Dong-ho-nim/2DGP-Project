from pico2d import *
import game_framework
import os
from state_machine import StateMachine
from pico2d import SDL_GetKeyboardState
import game_world

# 키 상태 실시간 가져오기 (매 프레임 갱신 위해 전역 변수로 선언)
keys = SDL_GetKeyboardState(None)

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'pain', path))

# 이벤트 체크
time_out = lambda e: e[0] == 'TIMEOUT'

# === 키 체크 람다 함수들 (완전히 수정 완료!) ===
# 1P 키
p1_left_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_a
p1_right_down    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_d
p1_down_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_s
p1_jump_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_k        # K = 점프
p1_weak_punch    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_j        # J = 약펀치
p1_kick          = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_l        # L = 킥
p1_strong_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and \
                            e[1].key==SDLK_j and keys[SDL_SCANCODE_S]                        # S + J = 강펀치

# 2P 키
p2_left_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_LEFT, SDLK_KP_4]
p2_right_down    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_RIGHT, SDLK_KP_6]
p2_down_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_DOWN, SDLK_KP_5]
p2_jump_down     = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_KP_2                    # KP_2 = 점프
p2_weak_punch    = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_1, SDLK_KP_7]       # KP_1 = 약펀치
p2_kick          = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_3, SDLK_KP_9]       # KP_3 = 킥
p2_strong_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and \
                            e[1].key in [SDLK_KP_1, SDLK_KP_7] and \
                            (keys[SDL_SCANCODE_DOWN] or keys[SDL_SCANCODE_KP_5])                   # ↓ + KP_1 = 강펀치

# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 5 * game_framework.frame_time * 8) % 5
    def draw(self):
        sx = int(self.frame) * 90
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 90, 95, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 90, 95, 0, 'h', self.p.x, self.p.y, 90, 95)

class Run:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_Run.png')
        self.frame = 0
        if (self.p.player==1 and p1_right_down(e)) or (self.p.player==2 and p2_right_down(e)):
            self.p.dir = self.p.face_dir = 1
        elif (self.p.player==1 and p1_left_down(e)) or (self.p.player==2 and p2_left_down(e)):
            self.p.dir = self.p.face_dir = -1
    def exit(self, e): self.p.dir = 0
    def do(self):
        self.frame = (self.frame + 6 * game_framework.frame_time * 6) % 6
        self.p.x += self.p.dir * 500 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        self.p.face_dir = self.p.dir
    def draw(self):
        sx = int(self.frame) * 86
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 86, 75, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 86, 75, 0, 'h', self.p.x, self.p.y, 86, 75)

class Jump:
    def __init__(self, p): self.p = p
    def enter(self, e):
        self.p.load_image('Pain_Jump.png')
        self.p.vy = 800
        if self.p.dir != 0: self.p.face_dir = self.p.dir
    def exit(self, e): self.p.y = 250
    def do(self):
        self.p.y += self.p.vy * game_framework.frame_time
        self.p.vy -= 2500 * game_framework.frame_time
        if self.p.y <= 250:
            self.p.y = 250
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, 60, 65, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(0, 0, 60, 65, 0, 'h', self.p.x, self.p.y, 60, 65)

class Punch:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Attack1.png'); self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 8 * game_framework.frame_time * 1.2
        if self.frame >= 7.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 93
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 93, 80, self.p.x + 30, self.p.y + 10)
        else:
            self.p.image.clip_composite_draw(sx, 0, 110, 80, 0, 'h', self.p.x - 30, self.p.y + 10, 110, 80)

class Kick:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Kick.png'); self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 10 * game_framework.frame_time * 1.8
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 150
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 150, 120, self.p.x + 40, self.p.y - 20)
        else:
            self.p.image.clip_composite_draw(sx, 0, 150, 120, 0, 'h', self.p.x - 40, self.p.y - 20, 150, 120)

class PowerAttack:  # 강펀치
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_PowerAttack.png')  # 이 파일 준비하세요!
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 8 * game_framework.frame_time * 2.0
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 116
        offset_x = 70 if self.p.face_dir == 1 else -70
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 116, 80, self.p.x + offset_x, self.p.y + 10)
        else:
            self.p.image.clip_composite_draw(sx, 0, 116, 80, 0, 'h', self.p.x + offset_x, self.p.y + 10, 116, 80)

class ShinraTensei:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Shinra.png'); self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 12 * game_framework.frame_time * 1.3
        if self.frame >= 11.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 220
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 220, 220, self.p.x, self.p.y + 100, 660, 660)
        else:
            self.p.image.clip_composite_draw(sx, 0, 220, 220, 0, 'h', self.p.x, self.p.y + 100, 660, 660)


# === 메인 클래스 Pain ===
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
        self.POWERATTACK = PowerAttack(self)   # ← 이름 통일
        self.SHINRA = ShinraTensei(self)

        def shinra_cmd(e):
            seq = ''.join(self.input_buffer[-3:])
            return (self.player==1 and p1_weak_punch(e) and seq in ['236', '263']) or \
                   (self.player==2 and p2_weak_punch(e) and seq in ['236', '263'])

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player==1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player==2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player==1 and p1_jump_down(e)) or (self.player==2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player==1 and p1_weak_punch(e)) or (self.player==2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player==1 and p1_kick(e)) or (self.player==2 and p2_kick(e)): self.KICK,
                lambda e: (self.player==1 and p1_strong_punch(e)) or (self.player==2 and p2_strong_punch(e)): self.POWERATTACK,
                shinra_cmd: self.SHINRA,
            },
            self.RUN: {
                lambda e: e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player==1 and p1_jump_down(e)) or (self.player==2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player==1 and p1_weak_punch(e)) or (self.player==2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player==1 and p1_kick(e)) or (self.player==2 and p2_kick(e)): self.KICK,
            },
            self.JUMP: {time_out: self.IDLE},
            self.PUNCH: {time_out: self.IDLE},
            self.KICK: {time_out: self.IDLE},
            self.POWERATTACK: {time_out: self.IDLE},
            self.SHINRA: {time_out: self.IDLE},
        })

    def load_image(self, name):
        self.image = load_resource(name)

    def update(self):
        global keys
        keys = SDL_GetKeyboardState(None)  # ← 매 프레임 갱신 필수!

        if self.state_machine.cur_state == self.RUN:
            self.face_dir = self.dir
        elif self.state_machine.cur_state == self.IDLE:
            from game_world import objects
            for layer in objects:
                for obj in layer:
                    if obj != self and isinstance(obj, Pain):
                        self.face_dir = 1 if obj.x > self.x else -1
                        break
                else: continue
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
            else:
                if key in [SDLK_DOWN, SDLK_KP_5]: self.input_buffer.append('2')
                elif key in [SDLK_RIGHT, SDLK_KP_6] and self.input_buffer[-1:] == ['2']: self.input_buffer.append('3')
                elif key in [SDLK_LEFT, SDLK_KP_4] and self.input_buffer[-1:] == ['2']: self.input_buffer.append('1')
                elif key in [SDLK_RIGHT, SDLK_KP_6]: self.input_buffer.append('6')
                elif key in [SDLK_LEFT, SDLK_KP_4]: self.input_buffer.append('4')
            if len(self.input_buffer) > 12:
                self.input_buffer = self.input_buffer[-12:]

        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(self.x-60, self.y-100, self.x+60, self.y+20)

    def get_bb(self):
        return self.x-60, self.y-100, self.x+60, self.y+20