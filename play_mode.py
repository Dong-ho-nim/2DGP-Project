from pico2d import *
from Player import Byakuya
from BackGround import BackGround

character = None
background = None

def enter():
    global character, background
    background = BackGround()
    character = Byakuya()

def exit():
    global character, background
    character = None
    background = None

def handle_event(event):
    if event.type == SDL_QUIT:
        import game_framework
        game_framework.quit()

def update():
    if background:
        background.update()
    if character:
        character.update()

def draw():
    clear_canvas()
    if background:
        background.draw()
    if character:
        character.draw()
    update_canvas()