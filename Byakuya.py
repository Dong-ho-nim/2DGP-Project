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


# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Byakuya_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 8 * game_framework.frame_time * 1) % 8
    def draw(self):
        sx = int(self.frame) * 66
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 66, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 66, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 66, 100)

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
            self.p.image.clip_draw(sx, 0, 71, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 71, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 71, 100)

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
            self.p.image.clip_draw(sx, 0, 111, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 111, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 111, 100)

class Attack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None

    def enter(self, e):
        self.p.load_image('Byakuya_Attack.png')
        self.frame = 0
        # 이펙트 생성 (5 프레임) - y 좌표 보정 적용
        self.effect = Effect(self.p.x, self.p.y + (100 / 2), 'Byakuya_Attack_Effect.png', 5, 135, 100)

    def exit(self, e):
        self.effect = None # 이펙트 소멸

    def do(self):
        # 캐릭터 애니메이션은 8프레임으로 진행
        self.frame += 8 * game_framework.frame_time * 1.5
        if self.frame >= 7.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        char_frame_index = int(self.frame)

        # 1. 캐릭터 그리기 (8 프레임) - y 좌표 보정 적용
        sx = char_frame_index * 130
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 130, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 130, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 130, 100)

        # 2. 이펙트 그리기 (캐릭터 프레임 1~5일 때만)
        if self.effect and 1 <= char_frame_index <= 5:
            # 이펙트 프레임을 캐릭터 프레임에 동기화
            effect_display_index = char_frame_index - 1
            
            # 위치를 캐릭터와 동일하게 설정 - Effect 객체 생성 시 이미 보정되었으므로 여기서는 변경하지 않음
            # self.effect.x, self.effect.y = self.p.x, self.p.y
            
            # 프레임 설정 및 그리기
            self.effect.frame = effect_display_index
            self.effect.draw(self.p.face_dir)
class PowerAttack:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None

    def enter(self, e):
        self.p.load_image('Byakuya_PowerAttack.png')
        self.frame = 0
        # 이펙트 생성 - y 좌표 보정 적용
        self.effect = Effect(self.p.x, self.p.y + (100 / 2), 'Byakuya_PowerAttack_Effect.png', 5, 165, 100)

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

        if self.effect and 1 <= char_frame_index <= 4:
            effect_display_index = char_frame_index - 1
            # Effect 객체 생성 시 이미 보정되었으므로 여기서는 변경하지 않음
            # self.effect.x, self.effect.y = self.p.x, self.p.y
            self.effect.frame = effect_display_index
            self.effect.draw(self.p.face_dir)

class Ultimate:
    Y_OFFSET = -205 # 시각적 조정을 위한 Y 오프셋 (510 높이의 중심을 100 높이의 캐릭터 중심에 맞추기 위해)

    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effect = None # 이펙트 추가
        self.hit_landed = False
        self.hit_checked = False

    def enter(self, e):
        self.p.load_image('Byakuya_Ultimate.png')
        self.frame = 0
        self.hit_landed = False
        self.hit_checked = False
        # Ultimate 이펙트 생성 (7 프레임, 250x250 가정)
        # 이펙트 y 위치는 캐릭터의 기본 y + (캐릭터 높이/2)에 얼라인
        self.effect = Effect(self.p.x + (self.p.face_dir * -50), self.p.y + (100 / 2) + 20, 'Byakuya_Ultimate_Effect.png', 12, 243, 180)


    def exit(self, e):
        self.effect = None # 이펙트 소멸

    def do(self):
        # Only check for hit once on the first active frame
        if not self.hit_checked and int(self.frame) >= 1:
            self.hit_checked = True
            attack_bb = self.p.get_attack_bb()
            if attack_bb:
                opponent_bb = self.p.opponent.get_bb()
                if opponent_bb and collide(attack_bb, opponent_bb):
                    self.hit_landed = True

        # Determine animation speed
        animation_speed_factor = 1.0  # Default speed
        
        # If the attack landed and we are in the last 4 frames, slow down
        if self.hit_landed and int(self.frame) >= 10:
            animation_speed_factor = 0.6

        self.frame += 14 * game_framework.frame_time * animation_speed_factor
        if self.frame >= 13.9: # 프레임 수에 맞춰 조건 변경 (0-13)
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
        
        if self.effect: # 이펙트 업데이트
            self.effect.update()

    def draw(self):
        char_frame_index = int(self.frame)

        # Byakuya_Ultimate.png의 프레임 크기: 너비 274, 높이 510
        # y 좌표는 다른 캐릭터 애니메이션과 동일하게 (높이 / 2) 보정 적용 후 Y_OFFSET 추가
        sx = char_frame_index * 266 # 프레임 너비 274로 변경
        draw_y = self.p.y + (510 / 2) + Ultimate.Y_OFFSET # Y_OFFSET 적용
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 266, 510, self.p.x, draw_y) # 너비 274, 높이 510으로 변경
        else:
            self.p.image.clip_composite_draw(sx, 0, 266, 510, 0, 'h', self.p.x, draw_y, 266, 510) # 너비 274, 높이 510으로 변경

        if self.effect and 1 <= char_frame_index <= 12:
            effect_display_index = char_frame_index - 1
            self.effect.frame = effect_display_index
            self.effect.draw(self.p.face_dir)


class Skill:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.effects = [] # 이펙트를 리스트로 관리

    def enter(self, e):
        self.p.load_image('Byakuya_Skill.png')
        self.frame = 0
        # 상대방 중심에서 x축으로 퍼져나가는 이펙트 생성
        if self.p.opponent:
            # 왼쪽으로 퍼지는 이펙트 - 상대방 y 좌표 보정 적용 (평균 높이 100 가정)# python
            class Effect:
                def __init__(self, x, y, image_name, frame_count, frame_w, frame_h, direction=0, move_speed=0, is_icon_effect=False, scale=1.0):
                    self.x, self.y = x, y
                    if is_icon_effect:
                        base_dir = os.path.dirname(__file__)
                        self.image = load_image(os.path.join(base_dir, 'Icon/images', image_name))
                    else:
                        self.image = load_resource(image_name)
                    self.frame = 0
                    self.frame_count = frame_count
                    self.frame_w = frame_w
                    self.frame_h = frame_h
                    self.scale = scale
                    self.speed = 1.5
                    self.direction = direction
                    self.move_speed = move_speed

                def update(self):
                    # 프레임 진행 및 자동 제거
                    self.frame = self.frame + self.frame_count * game_framework.frame_time * self.speed
                    if self.frame >= self.frame_count:
                        game_world.remove_object(self)
                    # 이동 처리(필요하면 사용)
                    if self.move_speed != 0:
                        self.x += self.direction * self.move_speed * game_framework.frame_time

                def draw(self, face_dir=1):
                    sx = int(self.frame) * self.frame_w
                    draw_w = int(self.frame_w * self.scale)
                    draw_h = int(self.frame_h * self.scale)
                    if face_dir == 1:
                        self.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.x, self.y, draw_w, draw_h)
                    else:
                        self.image.clip_composite_draw(sx, 0, self.frame_w, self.frame_h, 0, 'h', self.x, self.y, draw_w, draw_h)# python
                        class Skill:
                            def __init__(self, p):
                                self.p = p
                                self.frame = 0
                                self.effects = []

                            def enter(self, e):
                                self.p.load_image('Byakuya_Skill.png')
                                self.frame = 0
                                if self.p.opponent:
                                    # 스킬 이펙트 크기 키우려면 scale 값을 1.0 이상으로 설정
                                    big_scale = 1.8  # 예: 1.8배
                                    effect_left = Effect(self.p.opponent.x, self.p.opponent.y + (100 / 2), 'Byakuya_Skill_Effect.png', 5, 88, 8, direction=-1, move_speed=200, scale=big_scale)
                                    self.effects.append(effect_left)
                                    effect_right = Effect(self.p.opponent.x, self.p.opponent.y + (100 / 2), 'Byakuya_Skill_Effect.png', 5, 88, 8, direction=1, move_speed=200, scale=big_scale)
                                    self.effects.append(effect_right)

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

                                for effect in self.effects:
                                    if 1 <= char_frame_index <= 4:
                                        effect_display_index = char_frame_index - 1
                                        effect.frame = effect_display_index
                                        effect.draw(self.p.face_dir)
            effect_left = Effect(self.p.opponent.x, self.p.opponent.y + (100 / 2), 'Byakuya_Skill_Effect.png', 5, 88, 8, direction=-1, move_speed=200)
            self.effects.append(effect_left)
            # 오른쪽으로 퍼지는 이펙트 - 상대방 y 좌표 보정 적용 (평균 높이 100 가정)
            effect_right = Effect(self.p.opponent.x, self.p.opponent.y + (100 / 2), 'Byakuya_Skill_Effect.png', 5, 88, 8, direction=1, move_speed=200)
            self.effects.append(effect_right)


    def exit(self, e):
        self.effects.clear() # 이펙트 소멸

    def do(self):
        # Byakuya_Skill.png의 애니메이션 프레임은 10프레임으로 가정
        self.frame += 10 * game_framework.frame_time * 1.2
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))
        
        # 모든 이펙트 업데이트
        for effect in self.effects:
            effect.update()

    def draw(self):
        char_frame_index = int(self.frame)
        sx = char_frame_index * 82
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 82, 135, self.p.x, self.p.y + (135 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 82, 135, 0, 'h', self.p.x, self.p.y + (135 / 2), 82, 135)

        # 모든 이펙트 그리기
        for effect in self.effects:
            # 이펙트 프레임을 캐릭터 프레임에 동기화. 스킬 캐릭터 애니메이션의 특정 프레임에서 이펙트가 보이도록 설정
            # PowerAttack을 참고하여 1~4 프레임에서 이펙트가 보이도록 가정 (총 5프레임 이펙트)
            if 1 <= char_frame_index <= 4:
                effect_display_index = char_frame_index - 1
                effect.frame = effect_display_index
                effect.draw(self.p.face_dir)

class Jump:
    def __init__(self, p): self.p = p
    def enter(self, e):
        self.p.load_image('Byakuya_Jump.png')
        self.p.y_velocity = self.p.jump_speed  # 점프 시작 시 y 속도 설정
        self.p.jump_start_y = self.p.y # 점프 시작 높이 기록

    def exit(self, e):
        self.p.y_velocity = 0
        self.p.y = self.p.jump_start_y # 지면으로 y 위치 고정
        # Removed redundant state_machine.handle_state_event(('TIMEOUT', None)) as it's handled in do method

    def do(self):
        # 중력 적용
        self.p.y_velocity -= self.p.gravity * game_framework.frame_time
        self.p.y += self.p.y_velocity * game_framework.frame_time

        # 착지 확인
        if self.p.y <= self.p.jump_start_y:
            self.p.y = self.p.jump_start_y
            self.p.state_machine.handle_state_event(('TIMEOUT', None)) # 점프 종료

    def draw(self):
        # Byakuya_Jump.png is a single image, not a sprite sheet.
        # Assuming dimensions 66x100 based on previous context.
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, 61, 95, self.p.x, self.p.y + (95 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, 61, 95, 0, 'h', self.p.x, self.p.y + (95 / 2), 61, 95)


class Hit:
    def __init__(self, p):
        self.p = p
        self.duration = 0.5
        self.hit_effect = None

    def enter(self, e):
        self.p.load_image('Byakuya_Hit.png')
        self.duration = 0.5
        # Create the hit effect at this object's center (not opponent)
        effect_x = self.p.x
        effect_y = self.p.y + self.p.body_height / 2
        frame_width = 2192 // 16 # 137
        self.hit_effect = Effect(effect_x, effect_y, 'Hit_Effect.png', 16, frame_width, 200, is_icon_effect=True)
        game_world.add_object(self.hit_effect, 2) # Add to effect layer

    def exit(self, e):
        # Remove effect from game_world if still present
        if self.hit_effect:
            try:
                game_world.remove_object(self.hit_effect)
            except Exception:
                pass
            self.hit_effect = None

    def do(self):
        self.duration -= game_framework.frame_time
        if self.duration <= 0:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        # Assuming Byakuya_Hit.png is a single 80x100 image
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, 65, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, 65, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 65, 100)


# === 메인 클래스 Byakuya ===
class Byakuya:
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
            print(f"Byakuya hit! Health: {self.health}")
            if self.health <= 0:
                print("Byakuya is defeated!")

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
            if 1 <= frame_idx <= 5: # Attack frames where hitbox is active
                if self.face_dir == 1: # Facing right
                    return self.x + 10, self.y, self.x + 70, self.y + 80
                else: # Facing left
                    return self.x - 70, self.y, self.x - 10, self.y + 80
        elif state == self.POWERATTACK:
            try:
                frame_idx = int(state.frame)
            except Exception:
                return None
            if 1 <= frame_idx <= 4: # Power attack frames where hitbox is active
                if self.face_dir == 1: # Facing right
                    return self.x + 10, self.y, self.x + 70, self.y + 80
                else: # Facing left
                    return self.x - 70, self.y, self.x - 10, self.y + 80
        elif state == self.ULTIMATE:
            try:
                frame_idx = int(state.frame)
            except Exception:
                return None
            if int(state.frame) == 1 or (12 <= int(state.frame) <= 14): # Ultimate active frames
                width, height = 243, 180
                effect_x = self.x + (self.face_dir * 50)
                effect_y = self.y + (100 / 2) + 20
                return effect_x - width / 2, effect_y - height / 2, effect_x + width / 2, effect_y + height / 2
        elif state == self.SKILL:
            active_bbs = []
            for effect in state.effects:
                try:
                    frame_idx = int(state.frame)
                except Exception:
                    continue
                if 1 <= frame_idx <= 4: # Skill active frames
                    effect_width, effect_height = 88, 8
                    active_bbs.append((effect.x - effect_width / 2, effect.y - effect_height / 2,
                                       effect.x + effect_width / 2, effect.y + effect_height / 2))
            return active_bbs if active_bbs else None
        return None

    def set_opponent(self, opponent):
        self.opponent = opponent