from pico2d import *
import game_framework
import sys
import play_mode

# Constants
GRID_COLS = 2
GRID_ROWS = 2
GRID_START_X = 400
GRID_START_Y = 400
GRID_SPACING = 150

class Character:
    def __init__(self, name, icon_path, portrait_path):
        self.name = name
        self.icon = load_image(icon_path)
        self.portrait = load_image(portrait_path)

    def draw_icon(self, x, y, size=128):
        self.icon.draw(x, y, size, size)

    def draw_portrait(self, x, y, width=300, height=300):
        self.portrait.draw(x, y, width, height)

class AnimatedCursor:
    def __init__(self, frames, frame_rate):
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame = 0.0

    def update(self):
        self.current_frame = (self.current_frame + self.frame_rate * game_framework.frame_time) % len(self.frames)

    def draw(self, x, y, width=128, height=128):
        frame_to_draw = self.frames[int(self.current_frame)]
        frame_to_draw.draw(x, y, width, height)


# NEW - State and Constants
GRID_COLS = 4
GRID_ROWS = 4
GRID_START_X = 350
GRID_START_Y = 500
GRID_SPACING = 120
PORTRAIT_SIZE = 100

background = None
characters = [[]]
p1_cursor_pos = [0, 0]
p2_cursor_pos = [0, GRID_COLS - 1]
p1_cursor_anim = None
p2_cursor_anim = None
p1_selected_char = None
p2_selected_char = None
font = None

def enter():
    global background, characters, font
    global p1_cursor_pos, p2_cursor_pos, p1_cursor_anim, p2_cursor_anim
    global p1_selected_char, p2_selected_char

    background = load_image('Lobby/shapes/554.png')

    # Load Cursor Animations
    p1_frames = [load_image(f'Icon/sprites/DefineSprite_1473/{i}.png') for i in range(1, 21)]
    p2_frames = [load_image(f'Icon/sprites/DefineSprite_1476/{i}.png') for i in range(1, 21)]
    p1_cursor_anim = AnimatedCursor(p1_frames, 20)
    p2_cursor_anim = AnimatedCursor(p2_frames, 20)

    # Define the four selectable characters with their icon-to-portrait mapping
    character_data_map = {
        'Byakuya': {'icon': 'Icon/images/Byakuya_Icon.png', 'portrait': 'Icon/images/Byakuya_Picture.png'},
        'Naruto':  {'icon': 'Icon/images/Naruto_Icon.png', 'portrait': 'Icon/images/Naruto_Picture.png'},
        'Sado':    {'icon': 'Icon/images/Sado_Icon.png', 'portrait': 'Icon/images/Sado_Picture.png'},
        'Pain':    {'icon': 'Icon/images/Pain_Icon.png', 'portrait': 'Icon/images/Pain_Picture.png'}
    }

    # Create character objects
    char_data = [
        Character(name, data['icon'], data['portrait']) for name, data in character_data_map.items()
    ]
    
    # Arrange the 4 characters in the top row of the grid
    characters = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    for i, char in enumerate(char_data):
        if i < GRID_COLS:
            characters[0][i] = char

    # Reset state
    p1_cursor_pos = [0, 0]
    p2_cursor_pos = [0, GRID_COLS - 1]
    p1_selected_char = None
    p2_selected_char = None

def exit():
    global background, characters, font, p1_cursor_anim, p2_cursor_anim
    del background
    del characters
    if font:
        del font
    del p1_cursor_anim
    del p2_cursor_anim

def update():
    p1_cursor_anim.update()
    p2_cursor_anim.update()

def draw():
    clear_canvas()
    background.draw(600, 350, 1200, 700)

    # Draw P1's highlighted character portrait (left side)
    p1_highlighted_char = characters[p1_cursor_pos[0]][p1_cursor_pos[1]]
    if p1_highlighted_char:
        p1_highlighted_char.draw_portrait(200, 350, 300, 300)

    # Draw P2's highlighted character portrait (right side)
    p2_highlighted_char = characters[p2_cursor_pos[0]][p2_cursor_pos[1]]
    if p2_highlighted_char:
        p2_highlighted_char.draw_portrait(1000, 350, 300, 300)

    # Draw small selected icons at top-left
    if p1_selected_char:
        p1_selected_char.draw_icon(50, 650, 80)
    if p2_selected_char:
        p2_selected_char.draw_icon(150, 650, 80)

    # Draw character grid (bottom-center)
    grid_offset_x = 600 - (GRID_COLS * GRID_SPACING / 2) # Center the grid
    grid_offset_y = 100 # Position at the bottom
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = grid_offset_x + col * GRID_SPACING
            y = grid_offset_y - row * GRID_SPACING
            char = characters[row][col]
            if char:
                char.draw_icon(x, y, PORTRAIT_SIZE)

    # Draw P1 Cursor
    p1_x = grid_offset_x + p1_cursor_pos[1] * GRID_SPACING
    p1_y = grid_offset_y - p1_cursor_pos[0] * GRID_SPACING
    p1_cursor_anim.draw(p1_x, p1_y, 120, 120)

    # Draw P2 Cursor
    p2_x = grid_offset_x + p2_cursor_pos[1] * GRID_SPACING
    p2_y = grid_offset_y - p2_cursor_pos[0] * GRID_SPACING
    p2_cursor_anim.draw(p2_x, p2_y, 120, 120)

    update_canvas()

def handle_events(event):
    global p1_cursor_pos, p2_cursor_pos, p1_selected_char, p2_selected_char
    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE:
            game_framework.quit() # Or pop_mode if it exists

        # Player 1 Controls (WASD)
        if not p1_selected_char:
            if event.key == SDLK_d: # Right
                p1_cursor_pos[1] = (p1_cursor_pos[1] + 1) % 4 # Restrict to 4 columns
                p1_cursor_pos[0] = 0 # Keep in first row
            elif event.key == SDLK_a: # Left
                p1_cursor_pos[1] = (p1_cursor_pos[1] - 1 + 4) % 4 # Restrict to 4 columns
                p1_cursor_pos[0] = 0 # Keep in first row
            elif event.key == SDLK_s or event.key == SDLK_w: # Down/Up
                p1_cursor_pos[0] = 0 # Always keep in first row
            elif event.key == SDLK_j: # P1 Select
                char = characters[p1_cursor_pos[0]][p1_cursor_pos[1]]
                if char:
                    p1_selected_char = char
        elif event.key == SDLK_g: # P1 Deselect
            p1_selected_char = None

        # Player 2 Controls (Arrows)
        if not p2_selected_char:
            if event.key == SDLK_RIGHT:
                p2_cursor_pos[1] = (p2_cursor_pos[1] + 1) % 4 # Restrict to 4 columns
                p2_cursor_pos[0] = 0 # Keep in first row
            elif event.key == SDLK_LEFT:
                p2_cursor_pos[1] = (p2_cursor_pos[1] - 1 + 4) % 4 # Restrict to 4 columns
                p2_cursor_pos[0] = 0 # Keep in first row
            elif event.key == SDLK_DOWN or event.key == SDLK_UP: # Down/Up
                p2_cursor_pos[0] = 0 # Always keep in first row
            elif event.key == event.key == SDLK_b or event.key == SDLK_KP_1: # P2 Select
                char = characters[p2_cursor_pos[0]][p2_cursor_pos[1]]
                if char:
                    p2_selected_char = char
            elif event.key == SDLK_k: # P2 Deselect
                p2_selected_char = None

    # Check if both players have selected their characters after processing the event
    if p1_selected_char and p2_selected_char:
        # Pass selected character info to play_mode
        play_mode.p1_char_name = p1_selected_char.name
        play_mode.p2_char_name = p2_selected_char.name
        game_framework.change_mode(play_mode)
