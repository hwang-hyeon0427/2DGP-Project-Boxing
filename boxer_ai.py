from pico2d import *
from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action


class BoxerAI:
    """
    Boxer 객체에 붙어서 동작하는 AI 제어 전용 클래스.
    - 실제 좌표/상태머신/공격 등은 boxer 인스턴스를 통해 제어한다.
    """

    def __init__(self, boxer, level='easy'):
        self.boxer = boxer          # 실제로 움직일 Boxer
        self.level = level          # 'easy' / 'medium' / 'hard'
        self.bt = None              # BehaviorTree 루트

        # 이동 제어용
        self.move_dir = 0           # -1, 0, +1

        # 공격/가드 관련 상태
        self.last_attack_time = 0.0
        self.blocking = False
        self.block_start_time = 0.0
        self.block_hold_time = 0.0

        # BT 구성
        self.build_bt()

    # ----------------------------
    # AI용 가짜 키 이벤트 클래스
    # ----------------------------
    class _AIKeyEvent:
        def __init__(self, key_type, key_code):
            self.type = key_type
            self.key = key_code

    # ----------------------------
    # 키 입력 래퍼
    # ----------------------------
    def press_key(self, key_code):
        """
        가짜 SDL_KEYDOWN 이벤트를 만들어 Boxer.handle_event로 전달
        """
        from pico2d import SDL_KEYDOWN
        e = BoxerAI._AIKeyEvent(SDL_KEYDOWN, key_code)
        self.boxer.handle_event(e)

    def release_key(self, key_code):
        """
        가짜 SDL_KEYUP 이벤트를 만들어 Boxer.handle_event로 전달
        """
        from pico2d import SDL_KEYUP
        e = BoxerAI._AIKeyEvent(SDL_KEYUP, key_code)
        self.boxer.handle_event(e)

    # =======================
    # 상태 체크 헬퍼
    # =======================
    def can_act(self):
        """
        KO / Dizzy / Hurt 중이면 행동 불가
        """
        cur = self.boxer.state_machine.cur_state
        KOType = type(self.boxer.KO)
        DizzyType = type(self.boxer.DIZZY)
        HurtType = type(self.boxer.HURT)

        if isinstance(cur, (KOType, DizzyType, HurtType)):
            self.stop_move()
            return False
        return True

    def distance_to_opponent(self):
        if self.boxer.opponent is None:
            return None
        return self.boxer.opponent.x - self.boxer.x

    # =======================
    # 이동 관련
    # =======================
    def stop_move(self):
        """
        이동 중지: move_dir / xdir 0, 상태머신에 STOP 이벤트
        """
        if self.move_dir != 0:
            self.move_dir = 0
            self.boxer.xdir = 0
            # STOP 이벤트 (방향은 None or face_dir로 줄 수 있음)
            self.boxer.state_machine.handle_state_event(('STOP', None))

    def move_towards(self, dir):
        """
        dir: -1(왼쪽) / +1(오른쪽)
        """
        if dir == 0:
            self.stop_move()
            return

        if self.move_dir != dir:
            self.move_dir = dir
            self.boxer.xdir = dir
            self.boxer.face_dir = dir
            self.boxer.state_machine.handle_state_event(('WALK', None))

    # =======================
    # 공격 관련
    # =======================
    def in_attack_range(self):
        """
        난이도별 공격 사거리 계산
        """
        d = self.distance_to_opponent()
        if d is None:
            return False

        dx = abs(d)

        if self.level == 'easy':
            max_range = 150
        elif self.level == 'medium':
            max_range = 240
        else:
            max_range = 300   # hard: 더 멀리서도 공격

        return dx <= max_range

    def attack_random(self):
        """
        난이도별 공격 쿨타임, 공격 선택
        """
        now = get_time()

        # 난이도별 공격 쿨타임
        if self.level == 'easy':
            base_cd = 1.0
        elif self.level == 'medium':
            base_cd = 0.45
        else:
            base_cd = 0.22

        if now - self.last_attack_time < base_cd:
            return BehaviorTree.FAIL

        cur = self.boxer.state_machine.cur_state
        bad_types = (
            type(self.boxer.FRONT_HAND),
            type(self.boxer.REAR_HAND),
            type(self.boxer.UPPERCUT),
            type(self.boxer.BLOCK),
            type(self.boxer.BLOCK_ENTER),
            type(self.boxer.BLOCK_EXIT),
            type(self.boxer.HURT),
            type(self.boxer.DIZZY),
            type(self.boxer.KO)
        )

        if isinstance(cur, bad_types):
            return BehaviorTree.FAIL

        # 난이도 관계없이 버튼 매핑 동일
        if self.boxer.controls == 'wasd':
            front_key, rear_key, upper_key = SDLK_f, SDLK_g, SDLK_h
        else:
            front_key, rear_key, upper_key = SDLK_COMMA, SDLK_PERIOD, SDLK_SLASH

        import random
        choice = random.choice(['front', 'rear', 'upper'])
        if choice == 'front':
            self.press_key(front_key)
        elif choice == 'rear':
            self.press_key(rear_key)
        else:
            self.press_key(upper_key)

        self.last_attack_time = now
        return BehaviorTree.SUCCESS

    # =======================
    # 가드 관련
    # =======================
    def opponent_attacking(self):
        """
        상대가 공격 상태인지 체크
        """
        if self.boxer.opponent is None:
            return False

        opp_state = self.boxer.opponent.state_machine.cur_state
        FHType = type(self.boxer.opponent.FRONT_HAND)
        RHType = type(self.boxer.opponent.REAR_HAND)
        UType = type(self.boxer.opponent.UPPERCUT)

        return isinstance(opp_state, (FHType, RHType, UType))

    def do_guard(self):
        """
        난이도별 가드 확률 / 유지 시간
        """
        if self.boxer.controls == 'wasd':
            block_key = SDLK_r
        else:
            block_key = SDLK_SEMICOLON

        now = get_time()

        # 난이도별 가드 성능
        if self.level == 'easy':
            guard_prob = 0.20
            hold_time = 0.20
        elif self.level == 'medium':
            guard_prob = 0.55
            hold_time = 0.30
        else:
            guard_prob = 0.90
            hold_time = 0.50

        # 가드 시작
        if not self.blocking:
            import random
            if random.random() > guard_prob:
                return BehaviorTree.FAIL

            self.blocking = True
            self.block_start_time = now
            self.block_hold_time = hold_time

            self.stop_move()
            self.press_key(block_key)
            return BehaviorTree.RUNNING

        # 가드 유지
        else:
            if now - self.block_start_time >= self.block_hold_time:
                self.blocking = False
                self.release_key(block_key)
                return BehaviorTree.SUCCESS
            else:
                return BehaviorTree.RUNNING

    # =======================
    # KO 체크
    # =======================
    def is_ko(self):
        if isinstance(self.boxer.state_machine.cur_state, type(self.boxer.KO)):
            return BehaviorTree.SUCCESS
        return BehaviorTree.FAIL

    # =======================
    # 추격 로직
    # =======================
    def chase(self):
        if not self.can_act():
            return BehaviorTree.FAIL

        d = self.distance_to_opponent()
        if d is None:
            self.stop_move()
            return BehaviorTree.FAIL

        dx = abs(d)

        # 난이도별 적정 추격 거리
        if self.level == 'easy':
            stop_dist = 110
        elif self.level == 'medium':
            stop_dist = 70
        else:
            stop_dist = 35

        # 너무 가까우면 멈춤
        if dx < stop_dist:
            self.stop_move()
            return BehaviorTree.SUCCESS

        # 방향 결정
        if d > 0:
            self.move_towards(1)
        else:
            self.move_towards(-1)

        return BehaviorTree.RUNNING

    # =======================
    # BT용 래퍼 노드
    # =======================
    def bt_is_ko(self):
        return self.is_ko()

    def bt_in_attack_range(self):
        if not self.can_act():
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS if self.in_attack_range() else BehaviorTree.FAIL

    def bt_opponent_attacking(self):
        if not self.can_act():
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS if self.opponent_attacking() else BehaviorTree.FAIL

    def bt_attack_random(self):
        return self.attack_random()

    def bt_guard(self):
        return self.do_guard()

    def bt_chase(self):
        return self.chase()

    def bt_do_nothing(self):
        self.stop_move()
        return BehaviorTree.SUCCESS

    # =======================
    # Behavior Tree 구성
    # =======================
    def build_bt(self):
        ko_seq = Sequence(
            "KO Seq",
            Condition("Is KO", self.bt_is_ko),
            Action("Do Nothing", self.bt_do_nothing)
        )

        attack_seq = Sequence(
            "Attack Seq",
            Condition("In Attack Range", self.bt_in_attack_range),
            Action("Attack Random", self.bt_attack_random)
        )

        guard_seq = Sequence(
            "Guard Seq",
            Condition("Opponent Attacking", self.bt_opponent_attacking),
            Action("Guard", self.bt_guard)
        )

        chase_act = Action("Chase", self.bt_chase)

        root = Selector("AI Root", ko_seq, attack_seq, guard_seq, chase_act)
        self.bt = BehaviorTree(root)

    # =======================
    # 외부에서 호출할 진입 함수
    # =======================
    def set_level(self, level):
        self.level = level

    def update(self):
        """
        매 프레임 boxer.update() 안에서 호출됨
        """
        if self.bt is not None:
            self.bt.run()
