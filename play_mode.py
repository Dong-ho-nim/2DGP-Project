from pico2d import *
from Player import Byakuya
from BackGround import BackGround

character = None
background = None
sky = None

def enter():
    global character, background, sky
    background = BackGround()
    sky = Sky()
    character = Byakuya()

def exit():
    global character, background, sky
    character = None
    background = None
    sky = None

def handle_event(event):
    if event.type == SDL_QUIT:
        import game_framework
        game_framework.quit()

def update():
    if background:
        background.update()
    if sky:
        sky.update()
    if character:
        character.update()

def draw():
    clear_canvas()
    if background:
        background.draw()
    if sky:
        sky.draw()
    if character:
        character.draw()
    update_canvas()