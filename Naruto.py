# python
from pico2d import *
import game_framework
import os
from state_machine import StateMachine
from key_input_table import KEY_MAP
import game_world

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'Naruto', path))

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

class SkillEffect:
    def __init__(self, x, y, face_dir, image_name, frame_count, frame_w, frame_h):
        self.x, self.y = x, y
        self.face_dir = face_dir
        self.image = load_resource(image_name)
        self.frame_count = frame_count
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.frame = 0
        self.scale = 1.0
        # 부드러운 스케일링을 위한 타깃값과 속도
        self.target_scale = 1.0
        self.scale_speed = 6.0  # 클수록 더 빠르게 목표 스케일로 도달

    def update(self):
        # 프레임 애니메이션
        self.frame = (self.frame + self.frame_count * game_framework.frame_time * 2.0) % self.frame_count
        # 스케일 보간 (부드럽게 증감)
        if abs(self.scale - self.target_scale) > 1e-3:
            diff = self.target_scale - self.scale
            step = diff * min(1.0, self.scale_speed * game_framework.frame_time)
            self.scale += step

    def set_target_scale(self, s):
        self.target_scale = s

    def draw(self):
        sx = int(self.frame) * self.frame_w
        width = self.frame_w * self.scale
        height = self.frame_h * self.scale
        # 이미지 중심 기준으로 그리기 유지
        if self.face_dir == 1:
            self.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.x, self.y, width, height)
        else:
            self.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h', self.x, self.y, width, height)

# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Naruto_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 4 * game_framework.frame_time * 1) % 4
    def draw(self):
        sx = int(self.frame) * 88
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 88, 65, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 88, 65, 0, 'h', self.p.x, self.p.y + (100 / 2), 88, 65)

class Run:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Naruto_Run.png')
        self.frame = 0
        if (self.p.player==1 and p1_right_down(e)) or (self.p.player==2 and p2_right_down(e)):
            self.p.dir = self.p.face_dir = 1
        elif (self.p.player==1 and p1_left_down(e)) or (self.p.player==2 and p2_left_down(e)):
            self.p.dir = self.p.face_dir = -1
    def exit(self, e): self.p.dir = 0
    def do(self):
        self.frame = (self.frame + 6 * game_framework.frame_time * 2.5) % 6
        self.p.x += self.p.dir * 400 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        self.p.face_dir = self.p.dir
    def draw(self):
        sx = int(self.frame) * 84
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 84, 60, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 84, 60, 0, 'h', self.p.x, self.p.y + (100 / 2), 84, 60)

class Dash:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e):
        self.p.load_image('Naruto_Dash.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 2 * game_framework.frame_time * 5
        self.p.x += self.p.face_dir * 900 * game_framework.frame_time
        self.p.x = max(100, min(1100, self.p.x))
        if self.frame >= 1.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 78
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 78, 62, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 78, 62, 0, 'h', self.p.x, self.p.y + (100 / 2), 78, 62)

class Attack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
    def enter(self, e):
        self.p.load_image('Naruto_Attack.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 8 * game_framework.frame_time * 1.5
        if self.frame >= 7.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 103
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 103, 65, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 103, 65, 0, 'h', self.p.x, self.p.y + (100 / 2), 103, 65)

class PowerAttack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
    def enter(self, e):
        self.p.load_image('Naruto_PowerAttack.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 5 * game_framework.frame_time * 1.5
        if self.frame >= 4.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        sx = int(self.frame) * 97
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 97, 67, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 97, 67, 0, 'h', self.p.x, self.p.y + (100 / 2), 97, 67)

# Naruto Skill 상태 상수
SKILL_STATE_1 = 0
SKILL_STATE_2 = 1

class Skill:

    def __init__(self, p):

        self.p = p

        self.frame = 0

        self.state = SKILL_STATE_1

        self.effect = None

        self.state_timer = 0.0

        self.hit_on_first_frame = False

        self.scale_timer = 0.0

        self.scale_level = 0

        # 프레임별 손의 상대 위치 (x, y) 오프셋

        self.skill1_hand_offsets = [(30, 30), (32, 35), (35, 30), (33, 28)]

        self.skill2_hand_offsets = [(40, 40), (42, 45), (45, 40), (43, 38), (40, 42), (42, 45), (45, 40)]



    def enter(self, e):
        self.frame = 0
        self.state = SKILL_STATE_1
        self.p.load_image('Naruto_Skill1.png')
        self.effect = None
        self.hit_on_first_frame = False
        self.scale_level = 0
        self.scale_timer = 0.0
        self.is_paused_on_hit = False
        self.timeout_sent = False



    def exit(self, e):

        if self.effect:

            game_world.remove_object(self.effect)

        self.effect = None



    def do(self):
        face_dir = self.p.face_dir

        if self.state == SKILL_STATE_1:
            prev_frame = int(self.frame)
            self.frame = (self.frame + 4 * game_framework.frame_time * 1.5) % 4
            current_frame_int = int(self.frame)

            if current_frame_int >= 1:
                if self.effect is None:
                    offset_x = self.skill1_hand_offsets[current_frame_int][0] * face_dir
                    offset_y = self.skill1_hand_offsets[current_frame_int][1]
                    self.effect = SkillEffect(self.p.x + offset_x, self.p.y + offset_y, face_dir, 'Naruto_Skill_Effect1.png', 3, 33, 23)
                    game_world.add_object(self.effect, 1)
                else:
                    offset_x = self.skill1_hand_offsets[current_frame_int][0] * face_dir
                    offset_y = self.skill1_hand_offsets[current_frame_int][1]
                    self.effect.x = self.p.x + offset_x
                    self.effect.y = self.p.y + offset_y

            if prev_frame == 3 and current_frame_int == 0:
                self.state = SKILL_STATE_2
                self.frame = 0
                self.state_timer = 0.0
                self.p.load_image('Naruto_Skill2.png')

                if self.effect:
                    game_world.remove_object(self.effect)

                offset_x_2 = self.skill2_hand_offsets[0][0] * face_dir
                offset_y_2 = self.skill2_hand_offsets[0][1]
                self.effect = SkillEffect(self.p.x + offset_x_2, self.p.y + offset_y_2, face_dir, 'Naruto_Skill_Effect2.png', 7, 102, 85)
                game_world.add_object(self.effect, 1)

        elif self.state == SKILL_STATE_2:
            self.state_timer += game_framework.frame_time
            if not self.is_paused_on_hit:
                self.frame = (self.frame + 7 * game_framework.frame_time * 1.5)

            if self.frame < 1 and self.p.opponent:
                attack_bb = self.p.get_attack_bb()
                opponent_bb = self.p.opponent.get_bb()
                if attack_bb and opponent_bb and collide(attack_bb, opponent_bb):
                    self.hit_on_first_frame = True

            if self.hit_on_first_frame and self.frame >= 6:
                self.is_paused_on_hit = True

            if self.is_paused_on_hit:
                self.frame = 6 # 프레임 고정
                self.scale_timer += game_framework.frame_time
                if self.scale_level == 0:
                    if self.effect: self.effect.set_target_scale(1.35)
                    self.scale_level = 1
                elif self.scale_level == 1 and self.scale_timer > 0.08:
                    if self.effect: self.effect.set_target_scale(1.7)
                    self.scale_level = 2
                elif self.scale_level == 2 and self.scale_timer > 0.18:
                    if self.effect: self.effect.set_target_scale(2.2)
                    self.scale_level = 3
                elif self.scale_level == 3 and self.scale_timer > 0.35:
                    if not self.timeout_sent:
                        self.p.state_machine.handle_state_event(('TIMEOUT', None))
                        self.timeout_sent = True
            elif self.frame >= 7:
                 if not self.timeout_sent:
                        self.p.state_machine.handle_state_event(('TIMEOUT', None))
                        self.timeout_sent = True

            current_frame_int = int(self.frame) % 7
            offset_x = self.skill2_hand_offsets[current_frame_int][0] * face_dir
            offset_y = self.skill2_hand_offsets[current_frame_int][1]
            if self.effect:
                self.effect.x = self.p.x + offset_x
                self.effect.y = self.p.y + offset_y



    def draw(self):

        if self.state == SKILL_STATE_1:

            frame_w, frame_h = 120, 75

        else: # SKILL_STATE_2

            frame_w, frame_h = 121, 65



        sx = int(self.frame) * frame_w

        if self.p.face_dir == 1:

            self.p.image.clip_draw(sx, 0, frame_w, frame_h, self.p.x, self.p.y + frame_h / 2)

        else:

            self.p.image.clip_composite_draw(sx, 0, frame_w, frame_h, 0, 'h', self.p.x, self.p.y + frame_h/2, frame_w, frame_h)


class Ultimate:
    def __init__(self, p):
        self.p = p
        self.frame = 0
    def enter(self, e):
        self.p.load_image('Naruto_Idle.png')
        self.frame = 0
    def exit(self, e): pass
    def do(self):
        self.frame += 1 * game_framework.frame_time
        if self.frame >= 1:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        self.p.image.draw(self.p.x, self.p.y)


class Jump:
    def __init__(self, p): self.p = p
    def enter(self, e):
        self.p.load_image('Naruto_Jump.png')
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
            self.p.image.clip_draw(0, 0, 51, 72, self.p.x, self.p.y + (95 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, 51, 72, 0, 'h', self.p.x, self.p.y + (95 / 2), 51, 72)


# === 메인 클래스 Naruto ===
class Naruto:
    def __init__(self, player=1, x=200, y=250):
        self.player = player
        self.x, self.y = x, y
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.image = None
        self.pressed = set()
        self.input_buffer = []
        self.opponent = None
        self.effect = None

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
            },
            self.RUN: {
                lambda e: e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.ATTACK,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'SKILL': self.SKILL,
                lambda e: e[0] == 'ULTIMATE': self.ULTIMATE,
            },
            self.DASH: {time_out: self.IDLE},
            self.ATTACK: {time_out: self.IDLE},
            self.POWERATTACK: {time_out: self.IDLE},
            self.JUMP: {time_out: self.IDLE},
            self.SKILL: {time_out: self.IDLE},
            self.ULTIMATE: {time_out: self.IDLE},
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
            print(f"Naruto hit! Health: {self.health}")
            if self.health <= 0:
                print("Naruto is defeated!")

    def handle_event(self, event):
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
                    return self.x + 10, self.y, self.x + 30, self.y + 80
                else:
                    return self.x - 40, self.y, self.x - 10, self.y + 80
        elif state == self.POWERATTACK:
            if 1 <= int(state.frame) <= 4:
                if self.face_dir == 1:
                    return self.x , self.y, self.x + 40, self.y + 80
                else:
                    return self.x - 40, self.y, self.x + 30, self.y + 80
        elif state == self.ULTIMATE:
            if int(state.frame) == 1 or 12 <= int(state.frame) <= 14:
                width, height = 243, 180
                effect_x = self.x + (self.face_dir * 50)
                effect_y = self.y + (100 / 2) + 20
                return effect_x - width / 2, effect_y - height / 2, effect_x + width / 2, effect_y + height / 2
        elif state == self.SKILL:
            active_bbs = []
            if state.effect:
                effect_x, effect_y = state.effect.x, state.effect.y
                effect_w, effect_h = state.effect.frame_w, state.effect.frame_h
                active_bbs.append((effect_x - effect_w / 2, effect_y - effect_h / 2,
                                   effect_x + effect_w / 2, effect_y + effect_h / 2))
            return active_bbs if active_bbs else None
        return None

    def set_opponent(self, opponent):
        self.opponent = opponent