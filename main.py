from pico2d import open_canvas, close_canvas
import game_framework
import lobby_mode as start_mode
from Sound_Manager import sound_manager

open_canvas(1200, 700)
sound_manager.load_all()
game_framework.run(start_mode)
close_canvas()