from pico2d import *
from Player import Byakuya

character = None
background = None

def enter():
    global character, background
    character = Byakuya()
    background = load_image('background.png')  # 배경 이미지 불러오기

def exit():
    pass

def handle_event(event):
    if event.type == SDL_QUIT:
        import game_framework
        game_framework.quit()
    elif event.type == SDL_KEYDOWN:
        if event.key == SDLK_RIGHT:
            character.set_state("WalkRight")
        elif event.key == SDLK_LEFT:
            character.set_state("WalkLeft")
    elif event.type == SDL_KEYUP:
        if event.key in (SDLK_RIGHT, SDLK_LEFT):
            character.set_state("Idle")
    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_l:
            character.set_state("Teleport")

def update():
    character.update()

def draw():
    clear_canvas()
    background.draw(600, 350)   # 배경 먼저 그리기
    character.draw()            # 캐릭터 그리기
    update_canvas()