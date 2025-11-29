from pico2d import *
import math

import game_framework
import play_mode

# Sprite Animation Constants
NUM_CIRCLE_FRAMES = 9
ANIMATION_SPEED_PPS = 10 # 10 frames per second
EXPANSION_SPEED = 10 # Speed for the expanding image

# State
bg_image = None
bottom_right_image = None
top_left_image = None
center_image1 = None
center_image2 = None # This is Circle.png
below_center_image = None
vs_human_image = None
vs_cpu_image = None

circle_frame = 0
circle_frame_width = 71 # Set explicitly based on user input
center1_scale = 0.0

def enter():
    global bg_image, bottom_right_image, top_left_image
    global center_image1, center_image2, below_center_image
    global vs_human_image, vs_cpu_image
    global circle_frame, center1_scale
    
    bg_image = load_image('Lobby/shapes/554.png')
    bottom_right_image = load_image('Lobby/shapes/556.png')
    top_left_image = load_image('Lobby/shapes/558.png')
    center_image1 = load_image('Lobby/shapes/581.png')
    center_image2 = load_image('Lobby/shapes/Circle.png') # Circle.png sprite sheet
    vs_human_image = load_image('Lobby/shapes/587.png')
    vs_cpu_image = load_image('Lobby/shapes/589.png')
    below_center_image = load_image('Lobby/shapes/599.png')
    
    # Initialize animation variables
    circle_frame = 0
    center1_scale = 0.0


def exit():
    global bg_image, bottom_right_image, top_left_image
    global center_image1, center_image2, below_center_image
    global vs_human_image, vs_cpu_image
    
    del bg_image
    del bottom_right_image
    del top_left_image
    del center_image1
    del center_image2
    del below_center_image
    del vs_human_image
    del vs_cpu_image


def handle_events(event):
    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
        game_framework.quit()
    elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
        # vs Human 버튼 클릭 확인 (1200x700 캔버스에 맞게 좌표 수정)
        if 600 - 150 <= event.x <= 600 + 150 and 400 - 50 <= 700 - 1 - event.y <= 400 + 50:
            game_framework.change_mode(play_mode)


def update():
    global circle_frame, center1_scale
    # Update circle sprite animation
    circle_frame = (circle_frame + ANIMATION_SPEED_PPS * game_framework.frame_time) % NUM_CIRCLE_FRAMES

    # Update expanding image animation
    center1_scale += EXPANSION_SPEED * game_framework.frame_time
    if center1_scale > 20.0: # Reset when it gets very large
        center1_scale = 0.0


def draw():
    global circle_frame, center1_scale
    clear_canvas()
    
    # 1200x700 캔버스에 맞게 이미지 그리기
    bg_image.draw(600, 350, 1200, 700)
    
    # 오른쪽 아래, 왼쪽 위 (조정된 위치)
    bottom_right_image.draw(900, 200)
    top_left_image.draw(300, 500)
    
    # 중앙 확장 애니메이션 (581.png)
    width = center_image1.w * center1_scale
    height = center_image1.h * center1_scale
    center_image1.draw(600, 350, width, height)

    # Circle.png는 프레임 애니메이션으로 적용
    sx = int(circle_frame) * circle_frame_width
    center_image2.clip_draw(sx, 0, circle_frame_width, 71, 600, 350) # Use 71 for height

    # 버튼 (위치 유지)
    vs_human_image.draw(600, 400)
    vs_cpu_image.draw(600, 300)

    # 중앙보다 조금 더 아래 (위치 유지)
    below_center_image.draw(600, 150)
    
    update_canvas()

def pause():
    pass

def resume():
    pass
