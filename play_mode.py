from pico2d import *
import game_framework
import game_world
from Pain import Pain
from Byakuya import Byakuya
from BackGround import BackGround

p1 = None
p2 = None

def collide(bb1, bb2):
    left1, bottom1, right1, top1 = bb1
    left2, bottom2, right2, top2 = bb2
    if left1 > right2: return False
    if right1 < left2: return False
    if top1 < bottom2: return False
    if bottom1 > top2: return False
    return True

def enter():
    global p1, p2
    game_world.clear()
    game_world.add_object(BackGround(), 0)

    # p1 is Byakuya, p2 is Pain
    p1 = Byakuya(player=1, x=900, y=50)
    p2 = Pain(player=2, x=300, y=50)

    p1.set_opponent(p2)
    p2.set_opponent(p1)

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

    # --- Attack Collision Detection ---
    # Check p1's attack against p2's body
    p1_attack_bb = p1.get_attack_bb()
    if p1_attack_bb:
        p2_body_bb = p2.get_bb()
        
        # Handle cases where attack_bb can be a list (e.g., skill)
        if isinstance(p1_attack_bb, list):
            for bb in p1_attack_bb:
                if collide(bb, p2_body_bb) and not p2.invincible: # Check invincibility
                    print("P1 hit P2!")
                    p2.take_hit(10) # Reduce health
                    break # Only hit once per attack activation
        else:
            if collide(p1_attack_bb, p2_body_bb) and not p2.invincible: # Check invincibility
                print("P1 hit P2!")
                p2.take_hit(10) # Reduce health

    # Check p2's attack against p1's body
    p2_attack_bb = p2.get_attack_bb()
    if p2_attack_bb:
        p1_body_bb = p1.get_bb()
        
        # Handle cases where attack_bb can be a list (e.g., skill)
        if isinstance(p2_attack_bb, list):
            for bb in p2_attack_bb:
                if collide(bb, p1_body_bb) and not p1.invincible: # Check invincibility
                    print("P2 hit P1!")
                    p1.take_hit(10) # Reduce health
                    break # Only hit once per attack activation
        else:
            if collide(p2_attack_bb, p1_body_bb) and not p1.invincible: # Check invincibility
                print("P2 hit P1!")
                p1.take_hit(10) # Reduce health

    # game_world.handle_collisions() # Collision logic deferred

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

import lobby_mode