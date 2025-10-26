from pico2d import *
from state_machine import StateMachine

class Idle:
    def __init__(self, boxer):
        self.boxer = boxer


class Boxer:
    _img_cache = {}

    def __init__(self, cfg: dict):
        self.cfg = cfg

        spawn = cfg.get('spawn', {})
        self.x = spawn.get('x', 400)
        self.y = spawn.get('y', 90)
        self.face = spawn.get('face', 1)

        self.controls = cfg.get('controls', 'both')

        idle = cfg['idle']

        img_path = idle['image']
        if img_path not in Boxer._img_cache:
            Boxer._img_cache[img_path] = load_image(img_path)
        self.image = Boxer._img_cache[img_path]

        self.cols = int(idle['cols'])
        self.rows = int(idle.get('rows', 1))

        self.sheet_w = int(self.image.w)
        self.sheet_h = int(self.image.h)

        self.frame_w = self.sheet_w // self.cols
        self.frame_h = self.sheet_h // self.rows

        self.from_top = bool(idle.get('from_top', False))

        self.idle_row = int(idle.get('row', 0))
        if self.idle_row < 0:
            self.idle_row = 0
        if self.idle_row > self.rows - 1:
            self.idle_row = self.rows - 1

        self.scale = float(idle.get('scale', 1.0))

        self.frame = 0
        self.dir = 0

        self.IDLE = Idle(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    # 상태 전이 규칙 추가 예정
                }
            }
        )