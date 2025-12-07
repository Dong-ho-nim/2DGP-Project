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
    def __init__(self, x, y, image_name, frame_count, frame_w, frame_h, direction=0, move_speed=0, is_icon_effect=False):
        self.x, self.y = x, y
        if is_icon_effect:
            # Load from Icon/images folder
            base_dir = os.path.dirname(__file__)
            self.image = load_image(os.path.join(base_dir, 'Icon/images', image_name))
        else:
            # Load from character-specific folder
            self.image = load_resource(image_name)
        self.frame = 0
        self.frame_count = frame_count
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.speed = 1.5
        self.direction = direction
        self.move_speed = move_speed

    def update(self):
        self.frame = self.frame + self.frame_count * game_framework.frame_time * self.speed
        if self.frame >= self.frame_count:
            game_world.remove_object(self)

    def draw(self, face_dir=1): # Default face_dir to 1 for effects that don't need flipping
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
        self.is_paused_on_hit = False
        self.timeout_sent = False
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
                self.effect = SkillEffect(self.p.x + offset_x_2, self.p.y + offset_y_2, face_dir, 'Naruto_Skill_Effect2.png', 3, 31, 30)
                game_world.add_object(self.effect, 1)

        elif self.state == SKILL_STATE_2:
            self.state_timer += game_framework.frame_time
            if not self.is_paused_on_hit:
                self.frame = (self.frame + 7 * game_framework.frame_time * 1.5)

            current_frame_int = int(self.frame)
            # Adjust effect scale based on frame
            if self.effect:
                if current_frame_int == 2:
                    self.effect.set_target_scale(8.0)
                elif current_frame_int == 3:
                    self.effect.set_target_scale(16.0)
                elif current_frame_int == 4:
                    self.effect.set_target_scale(1.0)

            if self.frame >= 6.9: # Animation end condition
                if not self.timeout_sent:
                    self.p.state_machine.handle_state_event(('TIMEOUT', None))
                    self.timeout_sent = True

            if self.frame < 1 and self.p.opponent:
                attack_bb = self.p.get_attack_bb()
                opponent_bb = None
                if hasattr(self.p.opponent, 'get_bb'):
                    opponent_bb = self.p.opponent.get_bb()

                if attack_bb and opponent_bb:
                    hit = False
                    if isinstance(attack_bb, list):
                        for bb in attack_bb:
                            if collide(bb, opponent_bb):
                                hit = True
                                break
                    else:
                        if collide(attack_bb, opponent_bb):
                            hit = True
                    if hit:
                        self.hit_on_first_frame = True

    def draw(self):
        if self.state == SKILL_STATE_1:
            frame_w, frame_h = 120, 75
            sx = int(self.frame) * frame_w
            if self.p.face_dir == 1:
                self.p.image.clip_draw(sx, 0, frame_w, frame_h, self.p.x, self.p.y + (frame_h / 2))
            else:
                self.p.image.clip_composite_draw(sx, 0, frame_w, frame_h, 0, 'h', self.p.x, self.p.y + (frame_h / 2), frame_w, frame_h)
        elif self.state == SKILL_STATE_2:
            frame_w, frame_h = 121, 65
            sx = int(self.frame) * frame_w
            if self.p.face_dir == 1:
                self.p.image.clip_draw(sx, 0, frame_w, frame_h, self.p.x, self.p.y + (frame_h / 2))
            else:
                self.p.image.clip_composite_draw(sx, 0, frame_w, frame_h, 0, 'h', self.p.x, self.p.y + (frame_h / 2), frame_w, frame_h)

class UltimateEffect:
    def __init__(self, p):
        self.p = p
        self.image = load_resource('Naruto_Ultimate_Effect.png')
        
        self.y = 0
        self.start_x = 0
        self.current_width = 0
        self.effect_height = 30 # From user's previous request
        
        # Calculate maximum width based on player's position and direction
        left, _, right, _ = self.p.get_bb()
        if self.p.face_dir == 1:
            self.start_x = right
            self.max_width = 1200 - self.start_x
        else:
            self.start_x = left
            self.max_width = self.start_x - 0

        self.extend_speed = 3000 # pixels per second, this is the "speed" the user can adjust

    def update(self):
        # Extend the beam
        if self.current_width < self.max_width:
            self.current_width += self.extend_speed * game_framework.frame_time
            self.current_width = min(self.current_width, self.max_width)
        
        # Update y-position to follow player
        _, _, _, top = self.p.get_bb()
        self.y = top - 50 # Lowered position from user's request

    def draw(self):
        if self.current_width > 0:
            if self.p.face_dir == 1:
                center_x = self.start_x + self.current_width / 2
                self.image.draw(center_x, self.y, self.current_width, self.effect_height)
            else:
                center_x = self.start_x - self.current_width / 2
                self.image.draw(center_x, self.y, self.current_width, self.effect_height)

    def get_bb(self):
        if self.current_width > 0:
            if self.p.face_dir == 1:
                return self.start_x, self.y - self.effect_height / 2, self.start_x + self.current_width, self.y + self.effect_height / 2
            else:
                return self.start_x - self.current_width, self.y - self.effect_height / 2, self.start_x, self.y + self.effect_height / 2
        return None

class Ultimate:
    def __init__(self, p):
        self.p = p
        self.frame = 0.0
        self.frame_count = 7
        self.frame_w = 880 // 7
        self.frame_h = 95
        self.timeout_sent = False
        self.effect_created = False

    def enter(self, e):
        self.p.load_image('Naruto_Ultimate.png')
        self.frame = 0.0
        self.timeout_sent = False
        self.effect_created = False
        self.p.effect = None

    def exit(self, e):
        if self.p.effect:
            try:
                game_world.remove_object(self.p.effect)
            except ValueError:
                pass
            self.p.effect = None

    def do(self):
        self.frame += self.frame_count * game_framework.frame_time * 1.2
        
        # On the 6th frame, create the extending beam
        if not self.effect_created and int(self.frame) == 5:
            effect = UltimateEffect(self.p)
            game_world.add_object(effect, 1)
            self.p.effect = effect
            self.effect_created = True

        if self.frame >= self.frame_count:
            if not self.timeout_sent:
                self.p.state_machine.handle_state_event(('TIMEOUT', None))
                self.timeout_sent = True

    def draw(self):
        # Only draw Naruto. The effect will draw itself.
        sx = int(self.frame) * self.frame_w
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.p.x, self.p.y + (self.frame_h / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h',
                                             self.p.x, self.p.y + (self.frame_h / 2), self.frame_w, self.frame_h)

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





class Hit:
    def __init__(self, p):
        self.p = p
        self.duration = 0.5

    def enter(self, e):
        self.p.load_image('Naruto_Hit.png')
        self.duration = 0.5
        # Create the hit effect at this object's center
        effect_x = self.p.x
        effect_y = self.p.y + self.p.body_height / 2
        
        frame_width = 2192 // 16 # 137
        hit_effect = Effect(effect_x, effect_y, 'Hit_Effect.png', 16, frame_width, 200, is_icon_effect=True)
        game_world.add_object(hit_effect, 2) # Add to effect layer

    def exit(self, e):
        pass

    def do(self):
        self.duration -= game_framework.frame_time
        if self.duration <= 0:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        # Draw the character's Hit.png
        width, height = 55, 70
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, width, height, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, width, height, 0, 'h', self.p.x, self.p.y + (100 / 2), width, height)


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
        # 상태 머신 업데이트 및 무적 타이머 처리
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
            print(f"Naruto hit! Health: {self.health}")
            if self.health <= 0:
                print("Naruto is defeated!")

    def handle_event(self, event):
        # 상태가 HIT일 때 입력 무시
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
                elif key == SDLK_d:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('3')
                    else:
                        self.input_buffer.append('6')
                elif key == SDLK_a:
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.append('1')
                    else:
                        self.input_buffer.append('4') # Corrected from '6' to '4'


                elif key == SDLK_j:
                    if self.input_buffer and self.input_buffer[-1] == 'w':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SKILL', None))
                        return
                    if self.input_buffer and self.input_buffer[-1] == '2':
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('PowerAttack', None))
                        return
                    
                    seq = ''.join(self.input_buffer[-3:])
                    if seq in ['236', '263']:
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('ULTIMATE', None))
                        return
                elif key == SDLK_i:
                    self.input_buffer.clear()
                    self.state_machine.handle_state_event(('ULTIMATE', None))
                    return
            else: # Player 2
                # P2: 공격/얼티밋 우선 처리 (키패드 포함)
                if key in (KEY_MAP['P2']['ATTACK'], SDLK_KP_1):
                    # Hold 기반 분기: 아래 보유 -> PowerAttack, 위 보유 -> SKILL
                    if SDLK_DOWN in self.pressed or SDLK_KP_2 in self.pressed:
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('PowerAttack', None))
                        return
                    if SDLK_UP in self.pressed or SDLK_KP_8 in self.pressed:
                        self.input_buffer.clear()
                        self.state_machine.handle_state_event(('SKILL', None))
                        return
                    # else: 약공격은 기존 INPUT 이벤트로 처리

                # Ultimate: 메인 키 5 또는 키패드 5 모두 허용
                elif key in (KEY_MAP['P2']['ULTIMATE'], SDLK_KP_5, SDLK_5):
                    self.input_buffer.clear()
                    self.state_machine.handle_state_event(('ULTIMATE', None))
                    return

                # P2 방향키/버퍼 기록 (방향키와 키패드 유사 키 지원)
                if key in [SDLK_UP, SDLK_KP_8]:
                    self.input_buffer.append('8')
                elif key in [SDLK_DOWN, SDLK_KP_2]:
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
            if len(self.input_buffer) > 12:
                self.input_buffer = self.input_buffer[-12:]
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
        # debugging: draw bounding box (commented out to hide red BB)
        # draw_rectangle(*self.get_bb())
        attack_bb = self.get_attack_bb()
        if attack_bb:
            if isinstance(attack_bb, list):
                for bb in attack_bb:
                    # draw_rectangle(*bb)
                    pass
            else:
                # draw_rectangle(*attack_bb)
                pass

    def get_attack_bb(self):
        state = self.state_machine.cur_state
        if state == self.ATTACK:
            try:
                frame_idx = int(state.frame)
            except Exception:
                return None
            if 1 <= frame_idx <= 5:
                if self.face_dir == 1:
                    return self.x + 10, self.y, self.x + 30, self.y + 80
                else:
                    return self.x - 40, self.y, self.x - 10, self.y + 80
        elif state == self.POWERATTACK:
            try:
                frame_idx = int(state.frame)
            except Exception:
                return None
            if 1 <= frame_idx <= 4:
                if self.face_dir == 1:
                    return self.x , self.y, self.x + 40, self.y + 80
                else:
                    return self.x - 40, self.y, self.x + 30, self.y + 80
        elif state == self.ULTIMATE:
            if self.effect and hasattr(self.effect, 'get_bb'):
                return self.effect.get_bb()
            return None # No attack box if effect doesn't exist
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