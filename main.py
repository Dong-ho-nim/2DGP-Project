# main.py (이미 좋음)
from pico2d import open_canvas, close_canvas
import game_framework
import lobby_mode as start_mode

open_canvas(1200, 700)
game_framework.run(start_mode)
close_canvas()