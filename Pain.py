# python
from pico2d import *
import game_framework
import os
from state_machine import StateMachine
from pico2d import SDL_GetKeyboardState
import game_world
import random
import math
from key_input_table import KEY_MAP

# 키 상태 실시간 가져오기 (매 프레임 갱신 위해 전역 변수로 선언)
keys = SDL_GetKeyboardState(None)

# 리소스 로드
def load_resource(path):
    base_dir = os.path.dirname(__file__)
    return load_image(os.path.join(base_dir, 'pain', path))

# 이벤트 체크
time_out = lambda e: e[0] == 'TIMEOUT'

# Pain Ultimate Constants
ULTIMATE_STATE_START        = 0
ULTIMATE_STATE_STONE_SPAWN  = 1
ULTIMATE_STATE_STONE_COLLECT = 2
ULTIMATE_STATE_ATTACK       = 3

ULTIMATE_ANIM1_FRAMES = 3
ULTIMATE_ANIM1_W, ULTIMATE_ANIM1_H = 106, 90

ULTIMATE_ANIM2_FRAMES = 3
ULTIMATE_ANIM2_W, ULTIMATE_ANIM2_H = 106, 75

ULTIMATE_STONE_FRAMES = 3
ULTIMATE_STONE_W, ULTIMATE_STONE_H = 558, 277 # Total sprite sheet dimensions
ULTIMATE_STONE_FRAME_W = ULTIMATE_STONE_W // ULTIMATE_STONE_FRAMES # Single frame width
ULTIMATE_STONE_FRAME_H = ULTIMATE_STONE_H # Single frame height

MINI_STONE_COUNT_MAX = 10
MINI_STONE_SPAWN_DELAY = 0.05 # seconds between each mini stone spawn
MINI_STONE_COLLECT_SPEED = 200 # pixels per second
MINI_STONE_SIZE = 15 # px (이전 5 -> 보기 쉽게 증가)
MINI_STONE_MAX_DIST = 200 # Max spawn distance from Pain

ULTIMATE_STONE_FLY_SPEED = 400 # pixels per second
ULTIMATE_STONE_DISPLAY_SIZE = 400 # px, for when the stone flies towards opponent

# 1P
p1_left_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_a
p1_right_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_d
p1_jump_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_k
p1_weak_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_j
p1_dash        = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_l

# 2P
p2_left_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_LEFT]
p2_right_down  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_RIGHT]
p2_jump_down   = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key==SDLK_KP_2
p2_weak_punch  = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_1]
p2_dash        = lambda e: e[0]=='INPUT' and e[1].type==SDL_KEYDOWN and e[1].key in [SDLK_KP_3]

# === 상태 클래스들 ===
class Idle:
    def __init__(self, p): self.p = p; self.frame = 0
    def enter(self, e): self.p.load_image('Pain_Idle.png'); self.frame = 0
    def exit(self, e): pass
    def do(self): self.frame = (self.frame + 5 * game_framework.frame_time * 1) % 5
    def draw(self):
        sx = int(self.frame) * 88
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 88, 100, self.p.x, self.p.y + (100 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 88, 100, 0, 'h', self.p.x, self.p.y + (100 / 2), 88, 100)

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
            self.p.image.clip_draw(sx, 0, 86, 75, self.p.x, self.p.y + (75 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 86, 75, 0, 'h', self.p.x, self.p.y + (75 / 2), 86, 75)

class Jump:
    def __init__(self, p): self.p = p
    def enter(self, e):
        self.p.load_image('Pain_Jump.png')
        self.p.y_velocity = self.p.jump_speed  # Use character's jump speed
        if self.p.dir != 0: self.p.face_dir = self.p.dir
    def exit(self, e):
        self.p.y = self.p.jump_start_y # Snap to ground
        self.p.y_velocity = 0 # Reset vertical velocity on exit
    def do(self):
        # 중력 적용
        self.p.y_velocity -= self.p.gravity * game_framework.frame_time
        self.p.y += self.p.y_velocity * game_framework.frame_time

        # 착지 확인
        if self.p.y <= self.p.jump_start_y:
            self.p.y = self.p.jump_start_y
            self.p.y_velocity = 0 # Ensure velocity is zero on landing
            self.p.state_machine.handle_state_event(('TIMEOUT', None)) # 점프 종료
    def draw(self):
        if self.p.face_dir == 1:
            self.p.image.clip_draw(0, 0, 60, 65, self.p.x, self.p.y + (65 / 2))
        else:
            self.p.image.clip_composite_draw(0, 0, 60, 65, 0, 'h', self.p.x, self.p.y + (65 / 2), 60, 65)

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
            self.p.image.clip_draw(sx, 0, 93, 80, self.p.x + 30, self.p.y + (80 / 2) + 10) # y 보정 적용
        else:
            self.p.image.clip_composite_draw(sx, 0, 110, 80, 0, 'h', self.p.x - 30, self.p.y + (80 / 2) + 10, 110, 80) # y 보정 적용

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
            self.p.image.clip_draw(sx, 0, 70, 85, self.p.x, self.p.y + (85 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 70, 85, 0, 'h', self.p.x, self.p.y + (85 / 2), 70, 85)


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
            self.p.image.clip_draw(sx, 0, 116, 80, self.p.x + offset_x, self.p.y + (80 / 2) + 10)
        else:
            self.p.image.clip_composite_draw(sx, 0, 116, 80, 0, 'h', self.p.x + offset_x, self.p.y + (80 / 2) + 10, 116, 80)

class Ultimate: # Pain Ultimate
    def __init__(self, p):
        self.p = p
        self.frame = 0
        self.state = ULTIMATE_STATE_START
        self.ultimate_stone = None
        self.mini_stones = []
        self.mini_stone_spawn_timer = 0
        self.spawned_mini_stone_count = 0
        self.hit_opponent_flag = False

        self.ultimate_stone_img = None
        self.mini_stone1_img = None
        self.mini_stone2_img = None
        self.mini_stone3_img = None

    def enter(self, e):
        # Load images (store image objects)
        self.p.load_image('Pain_Ultimate1.png')
        self.ultimate_stone_img = load_resource('Pain_Ultimate_Stone.png')
        self.mini_stone1_img = load_resource('Mini_Stone1.png')
        self.mini_stone2_img = load_resource('Mini_Stone2.png')
        self.mini_stone3_img = load_resource('Mini_Stone3.png')

        self.frame = 0
        self.state = ULTIMATE_STATE_START
        self.ultimate_stone = None
        self.mini_stones = []
        self.mini_stone_spawn_timer = 0
        self.spawned_mini_stone_count = 0
        self.hit_opponent_flag = False

        # Create ultimate stone object (image object passed)
        # Place the stone slightly in front of Pain based on facing direction so it appears aligned visually
        offset_x = 120
        self.ultimate_stone = PainUltimateStone(self.p.x + self.p.face_dir * offset_x,
                                                self.p.y + self.p.body_height + (ULTIMATE_STONE_DISPLAY_SIZE/2),
                                                self.ultimate_stone_img)
        game_world.add_object(self.ultimate_stone, 2)

    def exit(self, e):
        if self.ultimate_stone:
            try:
                game_world.remove_object(self.ultimate_stone)
            except Exception:
                pass
        for stone in list(self.mini_stones):
            try:
                game_world.remove_object(stone)
            except Exception:
                pass
        self.ultimate_stone = None
        self.mini_stones = []
        self.p.load_image('Pain_Idle.png')

    def do(self):
        ANIMATION_SPEED = 8.0

        # Advance frame depending on state
        if self.state == ULTIMATE_STATE_START:
            self.frame += game_framework.frame_time * ANIMATION_SPEED
            if self.frame >= ULTIMATE_ANIM1_FRAMES:
                self.state = ULTIMATE_STATE_STONE_SPAWN
                self.frame = 0

        elif self.state == ULTIMATE_STATE_STONE_SPAWN:
            # animate Pain_Ultimate1
            self.frame = (self.frame + game_framework.frame_time * ANIMATION_SPEED) % ULTIMATE_ANIM1_FRAMES
            self.mini_stone_spawn_timer += game_framework.frame_time
            if self.mini_stone_spawn_timer >= MINI_STONE_SPAWN_DELAY and self.spawned_mini_stone_count < MINI_STONE_COUNT_MAX:
                stone_images = [self.mini_stone1_img, self.mini_stone2_img, self.mini_stone3_img]
                chosen_image = random.choice(stone_images)
                spawn_x = self.p.x + random.uniform(-MINI_STONE_MAX_DIST, MINI_STONE_MAX_DIST)
                spawn_y = self.p.y + random.uniform(self.p.body_height, self.p.body_height + MINI_STONE_MAX_DIST)
                # Pass the ultimate stone object as the target so mini stones track the stone's current position
                mini_stone = MiniStone(spawn_x, spawn_y, self.ultimate_stone, None, chosen_image, delay=0.0)
                self.mini_stones.append(mini_stone)
                game_world.add_object(mini_stone, 2)
                self.spawned_mini_stone_count += 1
                self.mini_stone_spawn_timer = 0

            # when all spawned and absorbed -> collect
            if self.spawned_mini_stone_count >= MINI_STONE_COUNT_MAX and all(not s.active for s in self.mini_stones):
                self.state = ULTIMATE_STATE_STONE_COLLECT
                self.frame = 0

        elif self.state == ULTIMATE_STATE_STONE_COLLECT:
            self.frame = (self.frame + game_framework.frame_time * ANIMATION_SPEED) % ULTIMATE_ANIM1_FRAMES
            all_collected = all(not s.active for s in self.mini_stones)
            if all_collected:
                self.state = ULTIMATE_STATE_ATTACK
                self.p.load_image('Pain_Ultimate2.png')
                self.frame = 0

        elif self.state == ULTIMATE_STATE_ATTACK:
            self.frame += game_framework.frame_time * ANIMATION_SPEED
            # start flying halfway through ultimate2 animation
            if self.ultimate_stone and not self.ultimate_stone.flying and self.frame >= (ULTIMATE_ANIM2_FRAMES * 0.5):
                if self.p.opponent:
                    self.ultimate_stone.start_flying(self.p.opponent.x, self.p.opponent.y + self.p.opponent.body_height/2)
                else:
                    self.ultimate_stone.start_flying(self.p.x + self.p.face_dir * 400, self.p.y + 100)

            if self.ultimate_stone and self.ultimate_stone.hit and not self.hit_opponent_flag:
                if self.p.opponent:
                    self.p.opponent.take_hit(30)
                self.hit_opponent_flag = True
                try:
                    game_world.remove_object(self.ultimate_stone)
                except Exception:
                    pass
                self.ultimate_stone = None

            if self.frame >= ULTIMATE_ANIM2_FRAMES and not self.ultimate_stone:
                self.p.state_machine.handle_state_event(('TIMEOUT', None))

        # update ultimate objects
        if self.ultimate_stone:
            if not self.ultimate_stone.flying:
                # keep the stone in front of Pain while charging
                offset_x = 120
                self.ultimate_stone.set_position(self.p.x + self.p.face_dir * offset_x,
                                                 self.p.y + self.p.body_height + (ULTIMATE_STONE_DISPLAY_SIZE/2))
            self.ultimate_stone.update()
        for s in list(self.mini_stones):
            s.update()

        # Update ultimate stone frame based on collected mini stones count
        if self.ultimate_stone:
            # Use different mapping depending on phase:
            # - During STONE_SPAWN: show growth according to spawned count (visual accumulation)
            # - During STONE_COLLECT / ATTACK: show progress according to collected count
            spawned = self.spawned_mini_stone_count
            collected = sum(1 for s in self.mini_stones if not s.active)
            if self.state == ULTIMATE_STATE_STONE_SPAWN:
                ratio = spawned / max(1, MINI_STONE_COUNT_MAX)
            else:
                ratio = collected / max(1, MINI_STONE_COUNT_MAX)

            idx = int(ratio * ULTIMATE_STONE_FRAMES)
            if idx >= ULTIMATE_STONE_FRAMES:
                idx = ULTIMATE_STONE_FRAMES - 1
            try:
                self.ultimate_stone.frame = idx
            except Exception:
                pass

    def draw(self):
        # draw Pain's ultimate animation frames
        img = self.p.image
        if not img:
            return
        if self.state in (ULTIMATE_STATE_START, ULTIMATE_STATE_STONE_SPAWN, ULTIMATE_STATE_STONE_COLLECT):
            w, h, frames = ULTIMATE_ANIM1_W, ULTIMATE_ANIM1_H, ULTIMATE_ANIM1_FRAMES
        else:
            w, h, frames = ULTIMATE_ANIM2_W, ULTIMATE_ANIM2_H, ULTIMATE_ANIM2_FRAMES
        sx = (int(self.frame) % frames) * w
        if self.p.face_dir == 1:
            img.clip_draw(sx, 0, w, h, self.p.x, self.p.y + (h/2))
        else:
            img.clip_composite_draw(sx, 0, w, h, 0, 'h', self.p.x, self.p.y + (h/2), w, h)

        # mini stones and ultimate stone are game world objects and will be drawn by game_world.render()


# Ultimate effect classes
class MiniStone:
    def __init__(self, x, y, target_x, target_y, image_obj, delay=0.0):
        self.x, self.y = x, y
        # target_x may be either a reference to the ultimate stone object or a numeric x coordinate
        # If target_x is an object with .x/.y, store as target_obj so the mini stone follows the moving stone
        if hasattr(target_x, 'x') and hasattr(target_x, 'y'):
            self.target_obj = target_x
            self.target_x = None
            self.target_y = None
        else:
            self.target_obj = None
            self.target_x, self.target_y = target_x, target_y
        self.image = image_obj
        self.delay = delay
        self.active = True if self.delay <= 0 else False
        self.speed = MINI_STONE_COLLECT_SPEED
        self.size = MINI_STONE_SIZE
        self.angle = 0.0

    def update(self):
        if self.delay > 0:
            self.delay -= game_framework.frame_time
            if self.delay <= 0:
                self.active = True
            return
        if not self.active:
            return
        # determine current target position (follow ultimate stone if provided)
        if self.target_obj is not None:
            tx, ty = self.target_obj.x, self.target_obj.y
        else:
            tx, ty = self.target_x, self.target_y

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist <= 1e-6:
            self.x, self.y = tx, ty
            self.active = False
            return
        travel = self.speed * game_framework.frame_time
        if dist <= travel:
            self.x, self.y = tx, ty
            self.active = False
        else:
            self.x += dx / dist * travel
            self.y += dy / dist * travel
        self.angle = (self.angle + game_framework.frame_time * 360) % 360

    def draw(self):
        if self.active or self.delay > 0:
            try:
                self.image.composite_draw(self.angle, '', self.x, self.y, self.size, self.size)
            except Exception:
                self.image.draw(self.x, self.y, self.size, self.size)


class PainUltimateStone:
    def __init__(self, x, y, image_obj):
        self.x, self.y = x, y
        self.image = image_obj
        self.frame_w = ULTIMATE_STONE_FRAME_W
        self.frame_h = ULTIMATE_STONE_FRAME_H
        self.size = ULTIMATE_STONE_DISPLAY_SIZE
        self.frame = 0
        self.flying = False
        self.target_x = 0
        self.target_y = 0
        self.hit = False

    def set_position(self, x, y):
        if not self.flying:
            self.x, self.y = x, y

    def start_flying(self, tx, ty):
        self.flying = True
        self.target_x, self.target_y = tx, ty

    def update(self):
        if self.flying and not self.hit:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            if dist <= 1e-6:
                self.x, self.y = self.target_x, self.target_y
                self.hit = True
                return
            travel = ULTIMATE_STONE_FLY_SPEED * game_framework.frame_time
            if dist <= travel:
                self.x, self.y = self.target_x, self.target_y
                self.hit = True
            else:
                self.x += dx / dist * travel
                self.y += dy / dist * travel

    def draw(self):
        if self.hit or not self.image:
            return
        try:
            # draw frame indicated by self.frame
            sx = int(self.frame) * self.frame_w
            self.image.clip_draw(sx, 0, self.frame_w, self.frame_h, self.x, self.y, self.size, self.size)
        except Exception:
            self.image.draw(self.x, self.y, self.size, self.size)

# --- Skill effect class 추가: Naruto의 SkillEffect와 유사하게 Pain용 이펙트 생성/갱신/드로우 처리 ---
# 해당 블록은 실수로 추가된 중복 구현입니다. 원래 Pain의 Skill 구현은 파일 상단에 이미 존재하므로
# 아래의 중복된 SkillEffect 및 Skill 클래스는 제거했습니다.


class Skill:
    def __init__(self, p):
        self.p = p
        self.frame = 0
        # 이동 관련
        self.move_timer = 0.0
        self.move_duration = 0.20
        self.move_speed = 300
        self.move_dir = 0

    def enter(self, e):
        self.p.load_image('Pain_Skill.png')
        self.frame = 0
        # 상대가 있으면 상대 좌표로 이동 (face_dir 반대 방향으로 약간 오프셋)
        if getattr(self.p, 'opponent', None) and getattr(self.p.opponent, 'face_dir', None) is not None:
            opp = self.p.opponent
            if opp.face_dir == 1:
                target_x = opp.x - 10
            else:
                target_x = opp.x + 10
            self.p.x = max(100, min(1100, target_x))
        else:
            self.move_dir = - self.p.face_dir
            self.move_timer = self.move_duration

    def exit(self, e):
        self.move_timer = 0.0
        self.move_dir = 0

    def do(self):
        if self.move_timer > 0:
            dx = self.move_dir * self.move_speed * game_framework.frame_time
            self.p.x += dx
            self.p.x = max(100, min(1100, self.p.x))
            self.move_timer -= game_framework.frame_time

        self.frame += 10 * game_framework.frame_time * 1.5
        if self.frame >= 9.9:
            self.p.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        sx = int(self.frame) * 100
        if self.p.face_dir == 1:
            self.p.image.clip_draw(sx, 0, 100, 85, self.p.x, self.p.y + (85 / 2))
        else:
            self.p.image.clip_composite_draw(sx, 0, 100, 85, 0, 'h', self.p.x, self.p.y + (85 / 2), 100, 85)

# === 메인 클래스 Pain ===
# python
class Pain:
    def __init__(self, player=1, x=600, y=250):
        self.player = player
        self.x, self.y = x, y
        self.face_dir = 1 if player == 1 else -1
        self.dir = 0
        self.image = None
        self.input_buffer = []
        self.pressed = set()
        self.opponent = None # 상대 객체 초기화

        self.jump_speed = 800 # Initial jump velocity (consistent with Pain's original value)
        self.gravity = 2500 # Gravity acceleration (consistent with Pain's original value)
        self.y_velocity = 0 # Vertical velocity for jumping
        self.jump_start_y = self.y # Ground level for jumping
        self.body_height = 100 # Assuming a standard body height for Y offset calculations (consistent with Byakuya)

        self.health = 100 # 체력
        self.invincible = False # 무적 상태
        self.hit_timer = 0.0 # 피격 후 무적 시간 카운터

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.PUNCH = Punch(self)
        self.DASH = Dash(self)
        self.POWERATTACK = PowerAttack(self)
        self.Ultimate = Ultimate(self)
        self.SKILL = Skill(self)  # Re-added Skill class instance

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {
                lambda e: (self.player == 1 and (p1_left_down(e) or p1_right_down(e))) or
                          (self.player == 2 and (p2_left_down(e) or p2_right_down(e))): self.RUN,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'Ultimate': self.Ultimate,
                lambda e: e[0] == 'SKILL': self.SKILL,  # Added SKILL transition
            },
            self.RUN: {
                lambda e: e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_a, SDLK_d, SDLK_LEFT, SDLK_RIGHT, SDLK_KP_4, SDLK_KP_6]: self.IDLE,
                lambda e: (self.player == 1 and p1_jump_down(e)) or (self.player == 2 and p2_jump_down(e)): self.JUMP,
                lambda e: (self.player == 1 and p1_weak_punch(e)) or (self.player == 2 and p2_weak_punch(e)): self.PUNCH,
                lambda e: (self.player == 1 and p1_dash(e)) or (self.player == 2 and p2_dash(e)): self.DASH,
                lambda e: e[0] == 'PowerAttack': self.POWERATTACK,
                lambda e: e[0] == 'Ultimate': self.Ultimate,
                lambda e: e[0] == 'SKILL': self.SKILL,  # Added SKILL transition
            },
            self.JUMP: {time_out: self.IDLE},
            self.PUNCH: {time_out: self.IDLE},
            self.DASH: {time_out: self.IDLE},
            self.POWERATTACK: {time_out: self.IDLE},
            self.Ultimate: {time_out: self.IDLE},
            self.SKILL: {time_out: self.IDLE},  # Added SKILL timeout transition
        })

    def load_image(self, name):
        self.image = load_resource(name)

    def update(self):
        # 실시간 키 상태 대신 handle_event에서 관리하는 self.pressed 사용
        if self.state_machine.cur_state in [self.IDLE, self.RUN]:
            # 방향 처리 유지
            if self.state_machine.cur_state == self.RUN:
                self.face_dir = self.dir

        self.state_machine.update()

        # 무적 시간 처리
        if self.invincible:
            self.hit_timer += game_framework.frame_time
            if self.hit_timer >= 0.5: # 0.5초 무적
                self.invincible = False
                self.hit_timer = 0.0

    def take_hit(self, damage):
        if not self.invincible:
            self.health -= damage
            self.invincible = True
            self.hit_timer = 0.0 # Reset timer
            print(f"Pain hit! Health: {self.health}")
            if self.health <= 0:
                print("Pain is defeated!")
                # 추가적인 사망 처리 로직 (애니메이션, 게임 오버 등)이 여기에 올 수 있습니다.

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
                        self.state_machine.handle_state_event(('Ultimate', None))
                        return
                elif key == SDLK_i: # Direct Ultimate trigger for P1
                    self.input_buffer.clear()
                    self.state_machine.handle_state_event(('Ultimate', None))
                    return
            else:
                # DEBUG: P2 관심 키(ATTACK/ULTIMATE/키패드) 입력 로그
                if key in (KEY_MAP['P2']['ATTACK'], KEY_MAP['P2']['ULTIMATE'], SDLK_KP_1, SDLK_KP_5, SDLK_5):
                    print(f"[DEBUG][P2] key={key}, pressed_set={self.pressed}")
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
                    self.state_machine.handle_state_event(('Ultimate', None))
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

            # 기존 INPUT 이벤트 전달
            self.state_machine.handle_state_event(('INPUT', event))

        elif event.type == SDL_KEYUP:
            # 키 해제 시 제거
            if event.key in self.pressed:
                self.pressed.remove(event.key)
            # 키업도 상태머신에 전달
            self.state_machine.handle_state_event(('INPUT', event))

    def get_bb(self):
        # 캐릭터의 일반적인 몸체 충돌 상자 (Idle 상태 기준)
        # x는 중앙, y는 바닥에 위치하므로,
        # left = self.x - width/2
        # bottom = self.y
        # right = self.x + width/2
        # top = self.y + height
        
        width = 88
        height = 100
        
        return self.x - width / 2 + 22, self.y - 10, self.x + width / 2 - 19, self.y + height + 10

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

        # Draw attack bounding box for debugging
        attack_bb = self.get_attack_bb()
        if attack_bb:
            draw_rectangle(*attack_bb)

    def get_attack_bb(self):
        state = self.state_machine.cur_state
        if state == self.PUNCH:
            # Pain_Attack1.png. Character clip_draw is 93x80 or 110x80
            # Active frames: 2 to 5
            if 2 <= int(state.frame) <= 5:
                # X offset from draw method: self.p.x + 30 (face_dir 1) and self.p.x - 30 (face_dir -1)
                # Y offset is (80 / 2) + 10 from self.p.y
                # bottom = self.y + 10
                
                width_right = 70
                width_left = 80
                height = 60
                offset_x = 20
                bottom_y = self.y + 10
                
                if self.face_dir == 1: # Facing right
                    # (self.x + offset_x) is the center of the drawn image
                    # so left = (self.x + offset_x) - width_right / 2
                    return (self.x + offset_x - width_right / 2, bottom_y,
                            self.x + offset_x + width_right / 2, bottom_y + height)
                else: # Facing left
                    # (self.x - offset_x) is the center of the drawn image
                    # so left = (self.x - offset_x) - width_left / 2
                    return (self.x - offset_x - width_left / 2, bottom_y,
                            self.x - offset_x + width_left / 2, bottom_y + height)
            
        elif state == self.POWERATTACK:
            # Pain_PowerAttack.png. Character clip_draw is 116x80
            # Active frames: 3 to 7
            if 3 <= int(state.frame) <= 7:
                # X offset from draw method: 70 * self.p.face_dir
                # Y offset is (80 / 2) + 10 from self.p.y
                # bottom = self.y + 10
                
                width = 90
                height = 60
                offset_x_val = 50 * self.face_dir
                bottom_y = self.y + 10
                
                return (self.x + offset_x_val - width / 2, bottom_y,
                        self.x + offset_x_val + width / 2, bottom_y + height)

        elif state == self.Ultimate: # Corrected placement
            if state.ultimate_stone and state.ultimate_stone.flying and not state.ultimate_stone.hit:
                # Return the bounding box of the flying ultimate stone
                stone_x, stone_y = state.ultimate_stone.x, state.ultimate_stone.y
                stone_size = state.ultimate_stone.size
                return (stone_x - stone_size / 2, stone_y - stone_size / 2,
                        stone_x + stone_size / 2, stone_y + stone_size / 2)

        elif state == self.SKILL:
            # Pain_Skill.png. Character clip_draw is 100x85
            # Active frames: 3 to 7
            if 3 <= int(state.frame) <= 7:
                # Draw position: self.p.x, self.p.y + (85 / 2)
                # Bottom of the image is self.y
                
                width = 100
                height = 85
                
                if self.face_dir == 1: # Facing right
                    # Assume skill starts at center x and extends right
                    return self.x - width / 2, self.y, self.x + width / 2, self.y + height
                else: # Facing left
                    # Assume skill starts at center x and extends left
                    return self.x - width / 2, self.y, self.x + width / 2, self.y + height
        
        return None # No attack active

    def set_opponent(self, opponent): # 상대 객체를 설정하는 메서드 추가
        self.opponent = opponent
