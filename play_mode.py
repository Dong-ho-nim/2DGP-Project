from pico2d import *
import game_framework
import game_world
from Pain import Pain
from Byakuya import Byakuya
from BackGround import BackGround

p1 = None
p2 = None

def enter():
    global p1, p2
    game_world.clear()
    game_world.add_object(BackGround(), 0)

    # p1 is Byakuya, p2 is Pain
    p1 = Byakuya(player=1, x=900)
    p2 = Pain(player=2, x=300)


    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)
    # game_world.add_collision_pair('p1:p2', p1, p2) # Collision logic deferred

def exit():
    game_world.clear()

def handle_events(event):
    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
        game_framework.change_mode(lobby_mode) # Go back to lobby
        
    if p1:
        p1.handle_event(event)
    if p2:
        p2.handle_event(event)

def update():
    game_world.update()
    # game_world.handle_collisions() # Collision logic deferred

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

import lobby_mode