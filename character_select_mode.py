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
    def __init__(self, name, image_path, portrait_coords):
        self.name = name
        self.image = load_image(image_path)
        self.portrait_coords = portrait_coords # (sx, sy, sw, sh)

    def draw_portrait(self, x, y):
        sx, sy, sw, sh = self.portrait_coords
        self.image.clip_draw(sx, sy, sw, sh, x, y, 128, 128)

# State
background = None
characters = []
p1_cursor = [0, 0] # [row, col]
p2_cursor = [0, 1] # [row, col]
p1_selected_char_name = None
p2_selected_char_name = None

def enter():
    global background, characters
    global p1_cursor, p2_cursor, p1_selected_char_name, p2_selected_char_name

    background = load_image('Lobby/shapes/554.png')
    
    # This list will be rebuilt each time, which is fine for now
    characters = [
        [ # Row 0
            Character('Naruto', 'DS _ DSi - Naruto_ Shinobi Rumble - Fighters - Naruto.png', (10, 150, 60, 60)),
            Character('Pain', 'DS _ DSi - Naruto_ Shinobi Rumble - Fighters - Pain.png', (10, 150, 60, 60))
        ],
        [ # Row 1
            Character('Byakuya', 'DS _ DSi - Bleach_ Dark Souls - Characters - Byakuya Kuchiki.png', (10, 430, 60, 60)),
            Character('Sado', 'DS _ DSi - Bleach_ Dark Souls - Characters - Yasutora Sado.png', (10, 200, 60, 60))
        ]
    ]
    p1_cursor = [0, 0]
    p2_cursor = [0, 1]
    p1_selected_char_name = None
    p2_selected_char_name = None

def exit():
    global background, characters
    del background
    del characters

def update():
    pass

def draw():
    clear_canvas()
    background.draw(600, 350, 1200, 700)

    # Draw character grid
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_START_X + col * GRID_SPACING
            y = GRID_START_Y - row * GRID_SPACING
            characters[row][col].draw_portrait(x, y)

    # Draw P1 Cursor
    p1_x = GRID_START_X + p1_cursor[1] * GRID_SPACING
    p1_y = GRID_START_Y - p1_cursor[0] * GRID_SPACING
    draw_rectangle(p1_x - 64, p1_y - 64, p1_x + 64, p1_y + 64, 255, 0, 0)

    # Draw P2 Cursor
    p2_x = GRID_START_X + p2_cursor[1] * GRID_SPACING
    p2_y = GRID_START_Y - p2_cursor[0] * GRID_SPACING
    draw_rectangle(p2_x - 66, p2_y - 66, p2_x + 66, p2_y + 66, 0, 0, 255)

    update_canvas()

def handle_events(event):
    global p1_cursor, p2_cursor, p1_selected_char_name, p2_selected_char_name

    if event.type == SDL_QUIT:
        game_framework.quit()
    elif event.type == SDL_KEYDOWN:
        if event.key == SDLK_ESCAPE:
            # Need to implement pop_mode in game_framework
            # For now, this will do nothing.
            pass

        # P1 Controls (Arrows)
        if p1_selected_char_name is None:
            if event.key == SDLK_DOWN:
                p1_cursor[0] = (p1_cursor[0] + 1) % GRID_ROWS
            elif event.key == SDLK_UP:
                p1_cursor[0] = (p1_cursor[0] - 1) % GRID_ROWS
            elif event.key == SDLK_RIGHT:
                p1_cursor[1] = (p1_cursor[1] + 1) % GRID_COLS
            elif event.key == SDLK_LEFT:
                p1_cursor[1] = (p1_cursor[1] - 1) % GRID_COLS
            elif event.key == SDLK_j:
                p1_selected_char_name = characters[p1_cursor[0]][p1_cursor[1]].name
                print(f"P1 selected: {p1_selected_char_name}")

        # P2 Controls (WASD)
        if p2_selected_char_name is None:
            if event.key == SDLK_s:
                p2_cursor[0] = (p2_cursor[0] + 1) % GRID_ROWS
            elif event.key == SDLK_w:
                p2_cursor[0] = (p2_cursor[0] - 1) % GRID_ROWS
            elif event.key == SDLK_d:
                p2_cursor[1] = (p2_cursor[1] + 1) % GRID_COLS
            elif event.key == SDLK_a:
                p2_cursor[1] = (p2_cursor[1] - 1) % GRID_COLS
            elif event.key == SDLK_1:
                p2_selected_char_name = characters[p2_cursor[0]][p2_cursor[1]].name
                print(f"P2 selected: {p2_selected_char_name}")

    # If P1 has selected, change to play_mode
    if p1_selected_char_name:
        game_framework.change_mode(play_mode)
