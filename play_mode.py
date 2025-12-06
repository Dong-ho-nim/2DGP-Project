from pico2d import *
from typing import Optional, Any
import game_framework
import game_world
import lobby_mode
from Pain import Pain
from Byakuya import Byakuya
from Naruto import Naruto
from Sado import Sado
from BackGround import BackGround

p1_char_name = None
p2_char_name = None

# Character image file paths
CHARACTER_ICONS = {
    'Pain': 'Icon/images/Pain_Icon.png',
    'Naruto': 'Icon/images/Naruto_Icon.png',
    'Byakuya': 'Icon/images/Byakuya_Icon.png',
    'Sado': 'Icon/images/Sado_Icon.png',
}

p1: Optional[Any] = None
p2: Optional[Any] = None
winner_player: Optional[Any] = None
loser_player: Optional[Any] = None


character_selection_background_image: Optional[Any] = None
p1_character_icon_image: Optional[Any] = None
p2_character_icon_image: Optional[Any] = None

# HUD 리소스
hp_frame_image: Optional[Any] = None
hp_fill_image: Optional[Any] = None
time_image: Optional[Any] = None
round_time: float = 0.0

# Game State 리소스
play_state = 'READY'
state_timer = 0.0
ready_image: Optional[Any] = None
go_image: Optional[Any] = None
k_image: Optional[Any] = None
o_image: Optional[Any] = None
winner_image: Optional[Any] = None


def collide(bb1, bb2):
    left1, bottom1, right1, top1 = bb1
    left2, bottom2, right2, top2 = bb2
    if left1 > right2: return False
    if right1 < left2: return False
    if top1 < bottom2: return False
    if bottom1 > top2: return False
    return True

def enter():
    global p1, p2, p1_char_name, p2_char_name, character_selection_background_image, p1_character_icon_image, p2_character_icon_image
    global hp_frame_image, hp_fill_image, time_image, round_time
    global play_state, state_timer, ready_image, go_image, k_image, o_image, winner_image
    global winner_player, loser_player

    game_world.clear()
    game_world.add_object(BackGround(), 0)

    character_selection_background_image = load_image('Icon/images/Icon_Frame.png')

    if p1_char_name is None: p1_char_name = 'Pain'
    if p2_char_name is None: p2_char_name = 'Naruto'
    
    p1_character_icon_image = load_image(CHARACTER_ICONS.get(p1_char_name))
    p2_character_icon_image = load_image(CHARACTER_ICONS.get(p2_char_name))

    # HUD 리소스 로드
    hp_frame_image = load_image('Icon/images/HP_Frame.png')
    hp_fill_image = load_image('Icon/images/HP.png')
    time_image = load_image('Icon/images/Time.png')
    
    # 게임 상태 리소스 로드
    ready_image = load_image('Icon/images/Ready.png')
    go_image = load_image('Icon/images/Go.png')
    k_image = load_image('Icon/images/K.png')
    o_image = load_image('Icon/images/O.png')
    winner_image = load_image('Icon/images/Winner.png')

    round_time = 99.0
    play_state = 'READY'
    state_timer = 0.0
    winner_player = None
    loser_player = None

    CHAR_CLASSES = {'Naruto': Naruto, 'Pain': Pain, 'Byakuya': Byakuya, 'Sado': Sado}
    p1_class = CHAR_CLASSES.get(p1_char_name, Byakuya)
    p2_class = CHAR_CLASSES.get(p2_char_name, Pain)

    p1 = p1_class(player=1, x=300, y=50)
    p2 = p2_class(player=2, x=900, y=50)

    p1.set_opponent(p2)
    p2.set_opponent(p1)

    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)

def exit():
    game_world.clear()

def handle_events(event):
    if play_state != 'PLAYING':
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(lobby_mode)
        return

    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
        game_framework.change_mode(lobby_mode)
        
    if p1: p1.handle_event(event)
    if p2: p2.handle_event(event)

def update():
    global play_state, state_timer, round_time, winner_player, loser_player

    if play_state == 'READY':
        state_timer += game_framework.frame_time
        if state_timer >= 1.5:
            play_state = 'GO'
            state_timer = 0.0
    elif play_state == 'GO':
        state_timer += game_framework.frame_time
        if state_timer >= 1.0:
            play_state = 'PLAYING'
    elif play_state == 'PLAYING':
        game_world.update()
        round_time -= game_framework.frame_time
        if round_time < 0: round_time = 0

        # 체력 체크
        if p1.health <= 0 or p2.health <= 0:
            winner_player = p2 if p1.health <= 0 else p1
            loser_player = p1 if p1.health <= 0 else p2
            play_state = 'KO'
            state_timer = 0.0
            # 패배한 플레이어는 게임 월드에서 제거
            game_world.remove_object(loser_player)
            return

        # 충돌 감지
        p1_attack_bb = p1.get_attack_bb()
        if p1_attack_bb:
            p2_body_bb = p2.get_bb()
            if isinstance(p1_attack_bb, list):
                for bb in p1_attack_bb:
                    if collide(bb, p2_body_bb) and not p2.invincible:
                        p2.take_hit(10); break
            elif collide(p1_attack_bb, p2_body_bb) and not p2.invincible:
                p2.take_hit(10)

        p2_attack_bb = p2.get_attack_bb()
        if p2_attack_bb:
            p1_body_bb = p1.get_bb()
            if isinstance(p2_attack_bb, list):
                for bb in p2_attack_bb:
                    if collide(bb, p1_body_bb) and not p1.invincible:
                        p1.take_hit(10); break
            elif collide(p2_attack_bb, p1_body_bb) and not p1.invincible:
                p1.take_hit(10)

    elif play_state == 'KO':
        state_timer += game_framework.frame_time
        if state_timer >= 1.0:
            play_state = 'WINNER'
            state_timer = 0.0
            if winner_player:
                # 승리 캐릭터의 상태를 IDLE로 강제 전환
                winner_player.state_machine.change_state(winner_player.IDLE)
    elif play_state == 'WINNER':
        if winner_player:
            # 승리 캐릭터의 IDLE 애니메이션을 업데이트
            winner_player.update()

        state_timer += game_framework.frame_time
        if state_timer >= 2.0:
            game_framework.change_mode(lobby_mode)

def draw_character_zoom(player, scale=2.0):
    if not player or not player.image:
        return
    
    # 캐릭터 상태에서 그리기 정보를 가져옵니다.
    # 각 캐릭터의 draw 메소드는 상태 머신을 통해 호출되므로, 현재 상태의 draw를 직접 호출하기는 어렵습니다.
    # 대신, 현재 상태의 프레임과 이미지를 기반으로 다시 그립니다.
    state = player.state_machine.cur_state
    if not hasattr(state, 'frame') or not hasattr(state, 'p'):
        return

    # 각 상태의 draw 메서드에서 프레임 계산 및 이미지 크기 정보를 가져와야 합니다.
    # 이는 상태별로 다르므로, 여기서는 일반적인 접근을 시도합니다.
    # 정확한 '줌'을 위해서는 모든 캐릭터의 모든 상태에 draw_zoomed 메서드를 추가하는 것이 좋습니다.
    # 여기서는 마지막 프레임의 모습을 간단히 확대하여 보여주는 것으로 대체합니다.
    
    try:
        # 이 부분은 각 캐릭터의 상태 draw 메소드 구현에 따라 매우 달라질 수 있습니다.
        # 일반화하기 어려운 부분으로, 우선 현재 x, y 위치에 크게 그리는 것으로 대체합니다.
        # 정확한 프레임별 스프라이트 시트 위치(sx)를 알 수 없으므로, 간단하게 첫 프레임을 그립니다.
        # 이상적으로는 player.state_machine.cur_state.draw_at(x,y,scale) 같은 함수가 필요합니다.
        dest_w, dest_h = player.image.w * scale, player.image.h * scale
        if hasattr(state, 'frame_w') and hasattr(state, 'frame_h'): # 프레임 정보가 있는 상태
             sx = int(state.frame) * state.frame_w
             player.image.clip_draw(sx, 0, state.frame_w, state.frame_h, get_canvas_width() // 2, get_canvas_height() // 2, state.frame_w * scale, state.frame_h * scale)
        else: # 기본 draw (전체 이미지)
            player.image.draw(get_canvas_width() // 2, get_canvas_height() // 2, dest_w, dest_h)

    except Exception as e:
        print(f"Error drawing zoom: {e}")


def draw():
    clear_canvas()
    game_world.render()
    
    # --- HUD ---
    frame_width, frame_height = 100, 100
    icon_width, icon_height = 60, 60
    p1_frame_x, p1_frame_y = 100, get_canvas_height() - 50
    p2_frame_x, p2_frame_y = get_canvas_width() - 100, get_canvas_height() - 50

    if character_selection_background_image:
        character_selection_background_image.draw(p1_frame_x, p1_frame_y, frame_width, frame_height)
    if p1_character_icon_image:
        p1_character_icon_image.draw(p1_frame_x, p1_frame_y, icon_width, icon_height)
    if character_selection_background_image:
        character_selection_background_image.draw(p2_frame_x, p2_frame_y, frame_width, frame_height)
    if p2_character_icon_image:
        p2_character_icon_image.draw(p2_frame_x, p2_frame_y, icon_width, icon_height)

    hp_w, hp_h = 200, 28
    hp_offset_y = 40

    if hp_frame_image: hp_frame_image.draw(p1_frame_x, p1_frame_y - hp_offset_y, hp_w, hp_h)
    if hp_fill_image and p1:
        hp_percent = max(0.0, min(1.0, p1.health / 100.0))
        fill_w = int(hp_w * hp_percent)
        if fill_w > 0:
            hp_fill_image.draw(p1_frame_x - (hp_w - fill_w) / 2, p1_frame_y - hp_offset_y, fill_w, hp_h)

    if hp_frame_image: hp_frame_image.draw(p2_frame_x, p2_frame_y - hp_offset_y, hp_w, hp_h)
    if hp_fill_image and p2:
        hp_percent = max(0.0, min(1.0, p2.health / 100.0))
        fill_w = int(hp_w * hp_percent)
        if fill_w > 0:
            hp_fill_image.draw(p2_frame_x - (hp_w - fill_w) / 2, p2_frame_y - hp_offset_y, fill_w, hp_h)

    if time_image: time_image.draw(get_canvas_width() // 2, get_canvas_height() - 50)
    if round_time >= 0:
        try:
            draw_font = load_font('ENCR10B.TTF', 24)
            time_text = f'{int(round_time)}'
            text_width, text_height = draw_font.get_size(time_text)
            draw_font.draw(get_canvas_width() // 2 - text_width // 2, get_canvas_height() - 50 - text_height//2, time_text,(255,255,0))
        except: pass

    # --- Game State Images ---
    if play_state == 'READY' and ready_image:
        ready_image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    elif play_state == 'GO' and go_image:
        go_image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    elif play_state == 'KO':
        if loser_player:
            draw_character_zoom(loser_player)
        if k_image and state_timer >= 0:
            k_image.draw(get_canvas_width() // 2 - 50, get_canvas_height() // 2)
        if o_image and state_timer >= 0.1:
            o_image.draw(get_canvas_width() // 2 + 50, get_canvas_height() // 2)
    elif play_state == 'WINNER':
        # 승리 캐릭터의 IDLE 애니메이션은 game_world.render()를 통해 그려지고,
        # 그 위에 'Winner' 이미지를 추가로 그립니다.
        if winner_image:
            winner_image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    
    update_canvas()
