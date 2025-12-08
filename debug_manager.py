DEBUG_EVENT = True        # 이벤트 로그
DEBUG_ATTACK = False       # 공격 상태 로그
DEBUG_HITBOX = False       # 히트박스 생성 로그
DEBUG_STATE = False        # 상태머신 로그
DEBUG_COLLISION = False    # 충돌 로그


def log(enabled, *msg):
    if enabled:
        print(*msg)
