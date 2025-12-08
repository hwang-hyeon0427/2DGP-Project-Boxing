from event_to_string import event_to_string
from debug_manager import log, DEBUG_STATE


class StateMachine:
    def __init__(self, start_state, rules: dict):
        self.cur_state = start_state
        self.rules = rules
        self.cur_state.enter(('START', 0))

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        if state_event[0] == 'ATTACK':
            attack_name = state_event[1]
            next_state = self.cur_state.boxer.ATTACK_ROUTER.route(attack_name)
            if next_state:
                self.cur_state.exit(state_event)
                next_state.enter(state_event)
                self.cur_state = next_state
            return
        for check_event in self.rules[self.cur_state].keys():
            if check_event(state_event):
                self.next_state = self.rules[self.cur_state][check_event]
                self.cur_state.exit(state_event)
                self.next_state.enter(state_event)
                log(DEBUG_STATE,f'State Change: {self.cur_state.__class__.__name__} ======= {event_to_string(state_event)}======= {self.next_state.__class__.__name__}')
                self.cur_state = self.next_state
                return

        if state_event[0] == 'INPUT':
            return
        log(DEBUG_STATE,f'처리되지 않은 이벤트 {event_to_string(state_event)}가 있습니다')


