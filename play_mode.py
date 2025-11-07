from pico2d import *
from Player import Byakuya

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

def update():
    character.update()

def draw():
    clear_canvas()
    character.draw()
    update_canvas()