from event_to_string import event_to_string
from debug_manager import debug


class StateMachine:
    def __init__(self, start_state, rules: dict):
        self.cur_state = start_state
        self.rules = rules

        # 초기 상태 진입
        debug.state(f"ENTER {self.cur_state.__class__.__name__} (initial)")
        self.cur_state.enter(('START', 0))

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        # 전체 이벤트 수신 로그
        debug.event(
            f"FSM EVENT RECEIVED: {state_event} | current={self.cur_state.__class__.__name__}"
        )

        # ------------------------------
        # ATTACK 전이는 특수 처리
        # ------------------------------
        if state_event[0] == 'ATTACK':
            attack_name = state_event[1]
            next_state = self.cur_state.boxer.ATTACK_ROUTER.route(attack_name)

            if next_state:
                debug.attack(
                    f"FSM ATTACK-TRANSITION: "
                    f"{self.cur_state.__class__.__name__} → {next_state.__class__.__name__} "
                    f"(attack={attack_name})"
                )

                self.cur_state.exit(state_event)
                next_state.enter(state_event)
                self.cur_state = next_state

            return

        # ------------------------------
        # 일반적인 이벤트 기반 상태 전이
        # ------------------------------
        for check_event in self.rules[self.cur_state].keys():
            if check_event(state_event):  # 조건을 만족한 전이
                next_state = self.rules[self.cur_state][check_event]

                debug.state(
                    f"TRANSITION: {self.cur_state.__class__.__name__} "
                    f"→ {next_state.__class__.__name__}  "
                    f"(event={event_to_string(state_event)})"
                )

                # 전이 수행
                self.cur_state.exit(state_event)
                next_state.enter(state_event)
                self.cur_state = next_state
                return

        # ------------------------------
        # INPUT 이벤트는 따로 처리하지 않음
        # ------------------------------
        if state_event[0] == 'INPUT':
            return

        # ------------------------------
        # 처리되지 않은 이벤트
        # ------------------------------
        debug.state(
            f"UNHANDLED EVENT: {event_to_string(state_event)} "
            f"in {self.cur_state.__class__.__name__}"
        )
