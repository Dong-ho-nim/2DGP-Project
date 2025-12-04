from pico2d import *
import game_framework
import game_world
from Pain import Pain
from Byakuya import Byakuya
from Naruto import Naruto
from Sado import Sado
from BackGround import BackGround

p1_char_name = None
p2_char_name = None

# Character icon clips within 1795.png (x, y, width, height)
# Assuming 1795.png is a sprite sheet with 80x80 icons
CHARACTER_ICON_CLIPS = {
    'Pain': (0, 0, 80, 80), # Placeholder values, will need actual layout
    'Naruto': (80, 0, 80, 80),
    'Byakuya': (160, 0, 80, 80),
    'Sado': (240, 0, 80, 80),
}

p1 = None
p2 = None

character_selection_sheet = None # This will hold the loaded 1795.png
p1_character_clip_info = None
p2_character_clip_info = None


def collide(bb1, bb2):
    left1, bottom1, right1, top1 = bb1
    left2, bottom2, right2, top2 = bb2
    if left1 > right2: return False
    if right1 < left2: return False
    if top1 < bottom2: return False
    if bottom1 > top2: return False
    return True

def enter():
    global p1, p2, p1_char_name, p2_char_name, character_selection_sheet, p1_character_clip_info, p2_character_clip_info # Ensure globals are declared
    game_world.clear()
    game_world.add_object(BackGround(), 0)

    # Load the character selection sprite sheet
    character_selection_sheet = load_image('Icon/images/1795.png')

    # Temporary hardcoding for p1_char_name and p2_char_name for testing
    # In a full game, these would be set by the character selection screen
    if p1_char_name is None: # Only set if not already set by selection screen
        p1_char_name = 'Pain'
    if p2_char_name is None: # Only set if not already set by selection screen
        p2_char_name = 'Naruto'
    
    # Get clipping information for selected characters
    p1_character_clip_info = CHARACTER_ICON_CLIPS.get(p1_char_name)
    p2_character_clip_info = CHARACTER_ICON_CLIPS.get(p2_char_name)

    CHAR_CLASSES = {
        'Naruto': Naruto,
        'Pain': Pain,
        'Byakuya': Byakuya,
        'Sado': Sado
        # Add other character classes here as they are created
    }

    # Default to Byakuya and Pain if names aren't found
    p1_class = CHAR_CLASSES.get(p1_char_name, Byakuya)
    p2_class = CHAR_CLASSES.get(p2_char_name, Pain)

    p1 = p1_class(player=1, x=300, y=50)
    p2 = p2_class(player=2, x=900, y=50)

    p1.set_opponent(p2)
    p2.set_opponent(p1)

    game_world.add_object(p1, 1)
    game_world.add_object(p2, 1)

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
    
    # Draw Player 1 icon (top-left)
    if character_selection_sheet and p1_character_clip_info:
        x, y, w, h = p1_character_clip_info
        character_selection_sheet.clip_draw(x, y, w, h, 100, get_canvas_height() - 50, 80, 80) # Adjust size as needed

    # Draw Player 2 icon (top-right)
    if character_selection_sheet and p2_character_clip_info:
        x, y, w, h = p2_character_clip_info
        character_selection_sheet.clip_draw(x, y, w, h, get_canvas_width() - 100, get_canvas_height() - 50, 80, 80) # Adjust size as needed

    update_canvas()
import lobby_mode