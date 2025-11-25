# play_mode.py
from pico2d import *
import game_framework
import game_world
from Pain import Pain
from BackGround import BackGround

p1 = p2 = None

def enter():
    global p1, p2
    game_world.clear()
    game_world.add_object(BackGround(), 0)
    p1 = Pain(player=1, x=300)
    p2 = Pain(player=2, x=900)
    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)
    game_world.add_collision_pair('p1:p2', p1, p2)

def handle_events(event):
    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type in (SDL_KEYDOWN, SDL_KEYUP):
        p1.handle_event(event)
        p2.handle_event(event)

def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()