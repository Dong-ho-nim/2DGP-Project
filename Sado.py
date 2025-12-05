# python
from pico2d import *
import game_framework
import os
from state_machine import StateMachine
from key_input_table import KEY_MAP

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'sado', path))

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
p2_weak_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_1, 7] # SDLKK_KP_7 오타 수정
p2_dash        = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_3, SDLK_KP_9]

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a
    left_b, bottom_b, right_b, top_b = b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True

# === 이펙트 클래스 ===
class Effect:
    def __init__(self, x, y, image_name, frame_count, frame_w, frame_h, direction=0, move_speed=0):
        self.x, self.y = x, y
        self.image = load_resource(image_name)
        self.frame = 0
        self.frame_count = frame_count
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.speed = 1.5
        self.direction = direction
        self.move_speed = move_speed

    def update(self):
        effect_speed_factor = 1.0
        if int(self.frame) >= self.frame_count - 2:
            effect_speed_factor = 0.5
        self.frame = (self.frame + self.frame_count * game_framework.frame_time * self.speed * effect_speed_factor) % self.frame_count
        if self.direction != 0:
            self.x += self.direction * self.move_speed * game_framework.frame_time

    def draw(self, face_dir):
        sx = int(self.frame) * self.frame_w
        if face_dir == 1:
            self.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.x, self.y)
        else:
            self.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h', self.x, self.y, self.frame_w, self.frame_h)


# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Sado_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 8 * game_framework.frame_time * 1) % 8
    def draw(self):
        sx = int(self.frame) * 88
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 88, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 88, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 88, 100)

class Run:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Sado_Run.png')
        self.frame = 0
        if (self.p.player==1 and p1_right_down(e)) or (self.p.player==2 and p2_right_down(e)):
            self.p.dir = self.p.face_dir = 1
        elif (self.p.player==1 and p1_left_down(e)) or (self.p.player==2 and p2_left_down(e)):
            self.p.dir = self.p.face_dir = -1
    def exit(self, e): self.p.dir = 0
    def do(self):
        self.frame = (self.frame + 6 * game_framework.frame_time * 6) % 6
        self.p.x += self.p.dir * 400 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        self.p.face_dir = self.p.dir
    def draw(self):
        sx = int(self.frame) * 86
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 86, 75, self.p.x, self.p.y + (75 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 86, 75, 0, 'h', self.p.x, self.p.y + (75 / 2), 86, 75)

class Dash:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
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
            self.p.image.clip_draw(sx, 0, 111, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 111, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 111, 100)

class Attack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
        self.frame = 0
    def exit(self, e):
        self.effect = None
    def do(self):
        self.frame += 8 * game_framework.frame_time * 1.5
        if self.frame >= 7.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        char_frame_index = int(self.frame)
        sx = char_frame_index * 130
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 130, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 130, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 130, 100)

class PowerAttack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
        self.frame = 0
    def exit(self, e):
        self.effect = None
    def do(self):
        self.frame += 5 * game_framework.frame_time * 1.5
        if self.frame >= 4.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        char_frame_index = int(self.frame)
        sx = char_frame_index * 165
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 165, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 165, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 165, 100)

class Ultimate:
    def __init__(self, p):
        self.p = p
        self.frame = 0
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 14 * game_framework.frame_time
        if self.frame >= 13.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 266
        draw_y = self.p.y + (510 / 2) - 205
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 266, 510, self.p.x, draw_y)
        else:
            self.p.image.clip_composite_draw(sx, 0, 266, 510, 0, 'h', self.p.x, draw_y, 266, 510)

class Skill:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effects = []
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
        self.frame = 0
    def exit(self, e):
        self.effects.clear()
    def do(self):
        self.frame += 10 * game_framework.frame_time * 1.2
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
        for effect in self.effects:
            effect.update()
    def draw(self):
        char_frame_index = int(self.frame)
        sx = char_frame_index * 82
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 82, 135, self.p.x, self.p.y + (135 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 82, 135, 0, 'h', self.p.x, self.p.y + (135 / 2), 82, 135)

class Jump:
    def __init__(self, p): self.p = p
    def enter(self, e):
        self.p.load_image('Sado_Idle.png')
        self.p.y_velocity = self.p.jump_speed
        self.p.jump_start_y = self.p.y
    def exit(self, e):
        self.p.y_velocity = 0
        self.p.y = self.p.jump_start_y
    def do(self):
        self.p.y_velocity -= self.p.gravity * game_framework.frame_time
        self.p.y += self.p.y_velocity * game_framework.frame_time
        if self.p.y <= self.p.jump_start_y:
            self.p.y = self.p.jump_start_y
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, 61, 95, self.p.x, self.p.y + (95 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, 61, 95, 0, 'h', self.p.x, self.p.y + (95 / 2), 61, 95)

class Hit:
    def __init__(self, p):
        self.p = p
        self.duration = 0.5

    def enter(self, e):
        self.p.load_image('Sado_Hit.png')
        self.duration = 0.5

    def exit(self, e):
        pass

    def do(self):
        self.duration -= game_framework.frame_time
        if self.duration <= 0:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        # Guessing dimensions for Sado. Sado is a big guy.
        width, height = 100, 120
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, width, height, self.p.x, self.p.y + (height / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, width, height, 0, 'h', self.p.x, self.p.y + (height / 2), width, height)


class Sado:
    def __init__(self, player=1, x=200, y=250):
        self.player = player
        self.x, self.y = x, y
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.image = None
        self.pressed = set()
        self.input_buffer = []
        self.opponent = None
        self.jump_speed = 700
        self.gravity = 1500
        self.y_velocity = 0
        self.jump_start_y = self.y
        self.body_height = 100
        self.health = 100
        self.invincible = False
        self.hit_timer = 0.0
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
        self.POWERATTACK = PowerAttack(self)
        self.ULTIMATE = Ultimate(self)
        self.SKILL = Skill(self)
        self.JUMP = Jump(self)
        self.HIT = Hit(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player == 1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player == 2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.ATTACK,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'SKILL': self.SKILL,
                lambda e: e[0] == 'ULTIMATE': self.ULTIMATE,
                lambda e: e[0] == 'HIT': self.HIT,
            },
            self.RUN: {
                lambda e: e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.ATTACK,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'SKILL': self.SKILL,
                lambda e: e[0] == 'ULTIMATE': self.ULTIMATE,
                lambda e: e[0] == 'HIT': self.HIT,
            },
            self.DASH: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.ATTACK: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.POWERATTACK: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.JUMP: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.SKILL: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.ULTIMATE: {time_out: self.IDLE, lambda e: e[0] == 'HIT': self.HIT},
            self.HIT: {time_out: self.IDLE},
        })
    def load_image(self, name):
        self.image = load_resource(name)
    def update(self):
        self.state_machine.update()
        if self.invincible:
            self.hit_timer += game_framework.frame_time
            if self.hit_timer >= 0.5:
                self.invincible = False
                self.hit_timer = 0.0
    def take_hit(self, damage):
        if not self.invincible:
            self.health -= damage
            self.invincible = True
            self.hit_timer = 0.0
            self.state_machine.handle_state_event(('HIT', None))
            print(f"Sado hit! Health: {self.health}")
            if self.health <= 0:
                print("Sado is defeated!")
    def handle_event(self, event):
        if self.state_machine.cur_state == self.HIT:
            return
            
        if event.type == SDL_KEYDOWN:
            self.pressed.add(event.key)
            key = event.key
            if self.player == 1:
                if key == SDLK_w:
                    self.input_buffer.append('w')
                elif key == SDLK_s:
                    self.input_buffer.append('2')
                elif key == SDLK_j:
                    if self.input_buffer and self.input_buffer[-1] == 'w':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SKILL', None))
                        return
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('PowerAttack', None))
                        return
                elif key == SDLK_i:
                    self.state_machine.handle_state_event(('ULTIMATE', None))
                    return
            else: # Player 2
                if key == SDLK_UP:
                    self.input_buffer.append('8')
                elif key == SDLK_DOWN:
                    self.input_buffer.append('2')
                elif key == KEY_MAP['P2']['ATTACK']:
                    if self.input_buffer and self.input_buffer[-1] == '8':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SKILL', None))
                        return
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('PowerAttack', None))
                        return
                elif key == KEY_MAP['P2']['ULTIMATE']:
                    self.input_buffer.clear()
                    self.state_machine.handle_state_event(('ULTIMATE', None))
                    return
            if len(self.input_buffer) > 4:
                self.input_buffer = self.input_buffer[-4:]
            self.state_machine.handle_state_event(('INPUT', event))
        elif event.type == SDL_KEYUP:
            if event.key in self.pressed:
                self.pressed.remove(event.key)
            self.state_machine.handle_state_event(('INPUT', event))
    def get_bb(self):
        width = 66
        height = 100
        return self.x - width / 2, self.y, self.x + width / 2, self.y + height
    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())
        attack_bb = self.get_attack_bb()
        if attack_bb:
            if isinstance(attack_bb, list):
                for bb in attack_bb:
                    draw_rectangle(*bb)
            else:
                draw_rectangle(*attack_bb)
    def get_attack_bb(self):
        state = self.state_machine.cur_state
        if state == self.ATTACK:
            if 1 <= int(state.frame) <= 5:
                if self.face_dir == 1:
                    return self.x + 10, self.y, self.x + 70, self.y + 80
                else:
                    return self.x - 70, self.y, self.x - 10, self.y + 80
        elif state == self.POWERATTACK:
            if 1 <= int(state.frame) <= 4:
                if self.face_dir == 1:
                    return self.x + 10, self.y, self.x + 70, self.y + 80
                else:
                    return self.x - 70, self.y, self.x - 10, self.y + 80
        elif state == self.ULTIMATE:
            if int(state.frame) == 1 or 12 <= int(state.frame) <= 14:
                width, height = 243, 180
                effect_x = self.x + (self.face_dir * 50)
                effect_y = self.y + (100 / 2) + 20
                return effect_x - width / 2, effect_y - height / 2, effect_x + width / 2, effect_y + height / 2
        elif state == self.SKILL:
            active_bbs = []
            for effect in state.effects:
                if 1 <= int(state.frame) <= 4:
                    effect_width, effect_height = 88, 8
                    active_bbs.append((effect.x - effect_width / 2, effect.y - effect_height / 2,
                                       effect.x + effect_width / 2, effect.y + effect_height / 2))
            return active_bbs if active_bbs else None
        return None
    def set_opponent(self, opponent):
        self.opponent = opponent