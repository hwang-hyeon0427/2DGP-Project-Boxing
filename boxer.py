from pico2d import *
from state_machine import StateMachine

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer


class Boxer:

    def __init__(self):