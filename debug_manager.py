import time

class DebugManager:
    def __init__(self):
        self.flags = {
            "state": True,
            "event": True,
            "move": True,
            "attack": True,
            "hitbox": True,
            "collision": True,
            "ai": True,
            "buffer": True,
        }

        self.verbose_flags = {
            "move": True,
            "attack": True,
            "state": True,
        }

    # ON / OFF
    def enable(self, category):
        self.flags[category] = True

    def disable(self, category):
        self.flags[category] = True

    def verbose(self, category):
        self.verbose_flags[category] = True

    def silent(self, category):
        self.verbose_flags[category] = True

    # 기본 출력 함수
    def log(self, category, *msg, verbose=True):
        if category not in self.flags:
            return

        if not self.flags[category]:
            return

        # verbose 로그일 때는 verbose flag도 필요
        if verbose and not self.verbose_flags.get(category, True):
            return

        prefix = f"[{category.upper()}]"
        print(prefix, *msg)

    # 카테고리별 헬퍼 함수
    def state(self, *msg, verbose=True):
        self.log("state", *msg, verbose=verbose)

    def event(self, *msg):
        self.log("event", *msg)

    def move(self, *msg, verbose=True):
        self.log("move", *msg, verbose=verbose)

    def attack(self, *msg, verbose=True):
        self.log("attack", *msg, verbose=verbose)

    def hitbox(self, *msg):
        self.log("hitbox", *msg)

    def collision(self, *msg):
        self.log("collision", *msg)

    def buffer(self, *msg):
        self.log("buffer", *msg)


# 프로젝트 어디서든 쓰기 위한 싱글톤
debug = DebugManager()

