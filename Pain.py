# python
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

# 1P
p1_left_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_a
p1_right_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_d
p1_jump_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_k
p1_weak_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_j
p1_dash        = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_l

# 2P
p2_left_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_LEFT, SDLK_KP_4]
p2_right_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_RIGHT, SDLK_KP_6]
p2_jump_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_KP_2
p2_weak_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_1, SDLK_KP_7]
p2_dash        = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_3, SDLK_KP_9]

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

class Dash:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_Dash.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 2 * game_framework.frame_time * 5  # Assuming 2 frames for dash animation
        self.p.x += self.p.face_dir * 800 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        if self.frame >= 1.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 70 # Assuming frame width is 88px for dash
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 70, 85, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 70, 85, 0, 'h', self.p.x, self.p.y, 70, 85)


class PowerAttack:  # 강펀치
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_PowerAttack.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 8 * game_framework.frame_time * 2.0
        if self.frame >= 9.9:
            self.frame = 0
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

class Skill:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Pain_Skill.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 10 * game_framework.frame_time * 1.5
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 100
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 100, 85, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 100, 85, 0, 'h', self.p.x, self.p.y, 100, 85)


# === 메인 클래스 Pain ===
# python
class Pain:
    def __init__(self, player=1, x=600):
        self.player = player
        self.x, self.y = x, 250
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.vy = 0
        self.image = None
        self.input_buffer = []
        # 눌린 키를 추적하는 집합 (이게 핵심)
        self.pressed = set()

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.PUNCH = Punch(self)
        self.DASH = Dash(self)
        self.POWERATTACK = PowerAttack(self)
        self.SHINRA = ShinraTensei(self)
        self.SKILL = Skill(self)

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player == 1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player == 2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'SHINRA': self.SHINRA,
                lambda e: e[0] == 'SKILL': self.SKILL,
            },
            self.RUN: {
                lambda e: e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'SHINRA': self.SHINRA,
                lambda e: e[0] == 'SKILL': self.SKILL,
            },
            self.JUMP: {time_out: self.IDLE},
            self.PUNCH: {time_out: self.IDLE},
            self.DASH: {time_out: self.IDLE},
            self.POWERATTACK: {time_out: self.IDLE},
            self.SHINRA: {time_out: self.IDLE},
            self.SKILL: {time_out: self.IDLE},
        })

    def load_image(self, name):
        self.image = load_resource(name)

    def update(self):
        # 실시간 키 상태 대신 handle_event에서 관리하는 self.pressed 사용
        if self.state_machine.cur_state in [self.IDLE, self.RUN]:
            if self.player == 2:
                if ((SDLK_DOWN in self.pressed) or (SDLK_KP_5 in self.pressed)) and \
                   ((SDLK_KP_1 in self.pressed) or (SDLK_KP_7 in self.pressed)):
                    self.state_machine.handle_state_event(('PowerAttack', None))

        # 방향 처리 유지
        if self.state_machine.cur_state == self.RUN:
            self.face_dir = self.dir

        self.state_machine.update()

    def handle_event(self, event):
        # KEYDOWN/KEYUP로 self.pressed를 업데이트해서 동시입력을 안정적으로 감지
        if event.type == SDL_KEYDOWN:
            self.pressed.add(event.key)
            key = event.key
            # 신라천정 입력버퍼 기록
            if self.player == 1:
                if key == SDLK_w:
                    self.input_buffer.append('w')
                elif key == SDLK_s:
                    self.input_buffer.append('2')
                elif key == SDLK_d:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('3')
                    else:
                        self.input_buffer.append('6')
                elif key == SDLK_a:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('1')
                    else:
                        self.input_buffer.append('4')
                elif key == SDLK_j:
                    # Skill: w -> j
                    if self.input_buffer and self.input_buffer[-1] == 'w':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SKILL', None))
                        return
                        
                    # PowerAttack: s -> j (input_buffer: '2')
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('PowerAttack', None))
                        return

                    seq = ''.join(self.input_buffer[-3:])
                    if seq in ['236', '263']:
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SHINRA', None))
                        return
            else:
                if key in [SDLK_DOWN, SDLK_KP_5]:
                    self.input_buffer.append('2')
                elif key in [SDLK_RIGHT, SDLK_KP_6]:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('3')
                    else:
                        self.input_buffer.append('6')
                elif key in [SDLK_LEFT, SDLK_KP_4]:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('1')
                    else:
                        self.input_buffer.append('4')
                elif key in [SDLK_KP_1, SDLK_KP_7]:
                    seq = ''.join(self.input_buffer[-3:])
                    if seq in ['236', '263']:
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SHINRA', None))
                        return

            if len(self.input_buffer) > 12:
                self.input_buffer = self.input_buffer[-12:]

            # 기존 INPUT 이벤트 전달
            self.state_machine.handle_state_event(('INPUT', event))

        elif event.type == SDL_KEYUP:
            # 키 해제 시 제거
            if event.key in self.pressed:
                self.pressed.remove(event.key)
            # 키업도 상태머신에 전달
            self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(self.x-60, self.y-100, self.x+60, self.y+20)

    def get_bb(self):
        return self.x-60, self.y-100, self.x+60, self.y+20
