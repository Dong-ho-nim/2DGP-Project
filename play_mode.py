import pico2d
from Player import Byakuya

character = None

def enter():
    global character
    character = Byakuya()

def exit():
    pass

def handle_event(event):
    if event.type == pico2d.SDL_QUIT:
        import game_framework
        game_framework.quit()

def update():
    character.update()

def draw():
    pico2d.clear_canvas()
    character.draw()
    pico2d.update_canvas()