from pico2d import *
import logo_mode as start_mode
import game_framework


open_canvas(317*4, 128*5)
game_framework.run(start_mode)
close_canvas()