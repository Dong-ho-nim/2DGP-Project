from pico2d import *
from player import Byakuya

character = None

def enter():
    global character
    character = Byakuya()

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

def update():
    character.update()

def draw():
    clear_canvas()
    character.draw()
    update_canvas()