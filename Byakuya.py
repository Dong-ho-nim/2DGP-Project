# python
from pico2d import *
import game_framework
import os
from state_machine import StateMachine

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'byakuya', path))

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

# === 이펙트 클래스 ===
class Effect:
    def __init__(self, x, y, image_name, frame_count, frame_w, frame_h):
        self.x, self.y = x, y
        self.image = load_resource(image_name)
        self.frame = 0
        self.frame_count = frame_count
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.speed = 1.5

    def update(self):
        self.frame = (self.frame + self.frame_count * game_framework.frame_time * self.speed) % self.frame_count

    def draw(self, face_dir):
        sx = int(self.frame) * self.frame_w
        if face_dir == 1:
            self.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.x, self.y)
        else:
            self.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h', self.x, self.y, self.frame_w, self.frame_h)


# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Byakuya_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 8 * game_framework.frame_time * 1) % 8
    def draw(self):
        sx = int(self.frame) * 66
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 66, 100, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 66, 100, 0, 'h', self.p.x, self.p.y, 66, 100)

class Run:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Byakuya_Run.png')
        self.frame = 0
        if (self.p.player==1 and p1_right_down(e)) or (self.p.player==2 and p2_right_down(e)):
            self.p.dir = self.p.face_dir = 1
        elif (self.p.player==1 and p1_left_down(e)) or (self.p.player==2 and p2_left_down(e)):
            self.p.dir = self.p.face_dir = -1
    def exit(self, e): self.p.dir = 0
    def do(self):
        self.frame = (self.frame + 4 * game_framework.frame_time * 6) % 4
        self.p.x += self.p.dir * 400 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        self.p.face_dir = self.p.dir
    def draw(self):
        sx = int(self.frame) * 71
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 71, 100, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 71, 100, 0, 'h', self.p.x, self.p.y, 71, 100)

class Dash:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Byakuya_Dash.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 2 * game_framework.frame_time * 5
        self.p.x += self.p.face_dir * 900 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        if self.frame >= 1.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 111
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 111, 100, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 111, 100, 0, 'h', self.p.x, self.p.y, 111, 100)

class Attack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None

    def enter(self, e):
        self.p.load_image('Byakuya_Attack.png')
        self.frame = 0
        # 이펙트 생성 (5 프레임)
        self.effect = Effect(self.p.x, self.p.y, 'Byakuya_Attack_Effect.png', 5, 135, 100)

    def exit(self, e):
        self.effect = None # 이펙트 소멸

    def do(self):
        # 캐릭터 애니메이션은 8프레임으로 진행
        self.frame += 8 * game_framework.frame_time * 1.5
        if self.frame >= 7.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        char_frame_index = int(self.frame)

        # 1. 캐릭터 그리기 (8 프레임)
        sx = char_frame_index * 130
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 130, 100, self.p.x, self.p.y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 130, 100, 0, 'h', self.p.x, self.p.y, 130, 100)

        # 2. 이펙트 그리기 (캐릭터 프레임 1~5일 때만)
        if self.effect and 1 <= char_frame_index <= 5:
            # 이펙트 프레임을 캐릭터 프레임에 동기화
            effect_display_index = char_frame_index - 1
            
            # 위치를 캐릭터와 동일하게 설정
            self.effect.x, self.effect.y = self.p.x, self.p.y
            
            # 프레임 설정 및 그리기
            self.effect.frame = effect_display_index
            self.effect.draw(self.p.face_dir)

# === 메인 클래스 Byakuya ===
class Byakuya:
    def __init__(self, player=1, x=200):
        self.player = player
        self.x, self.y = x, 250
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.image = None
        self.pressed = set()

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
        # TODO: Add other states like Jump

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player == 1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player == 2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.ATTACK,
            },
            self.RUN: {
                lambda e: e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.ATTACK,
            },
            self.DASH: {time_out: self.IDLE},
            self.ATTACK: {time_out: self.IDLE},
        })

    def load_image(self, name):
        self.image = load_resource(name)

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        if event.type in [SDL_KEYDOWN, SDL_KEYUP]:
            if event.type == SDL_KEYDOWN:
                self.pressed.add(event.key)
            elif event.key in self.pressed:
                self.pressed.remove(event.key)
            self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        # Placeholder Bounding Box
        return self.x-50, self.y-50, self.x+50, self.y+50
