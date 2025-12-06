# state_machine.py
class StateMachine:
    def __init__(self, start_state, transitions):
        # start_state: 상태 인스턴스 (예: self.IDLE)
        # transitions: {state_instance: {check_fn: next_state_instance, ...}, ...}
        self.cur_state = start_state
        self.transitions = transitions
        # 시작 상태의 enter 호출
        try:
            if hasattr(self.cur_state, 'enter'):
                self.cur_state.enter(('START', None))
        except Exception:
            pass

    def update(self):
        if self.cur_state and hasattr(self.cur_state, 'do'):
            try:
                self.cur_state.do()
            except Exception:
                pass

    def draw(self):
        if self.cur_state and hasattr(self.cur_state, 'draw'):
            try:
                self.cur_state.draw()
            except Exception:
                pass

    def handle_state_event(self, event):
        # event는 ('INPUT', e) 또는 ('TIMEOUT', 0) 등이다.
        if not self.cur_state:
            return
        # 현재 상태에 대한 전이 테이블 조회
        table = self.transitions.get(self.cur_state, {})
        for check_fn, next_state in table.items():
            try:
                if check_fn(event):
                    # exit 호출
                    try:
                        if hasattr(self.cur_state, 'exit'):
                            self.cur_state.exit(event)
                    except Exception:
                        pass
                    # 상태 전환
                    self.cur_state = next_state
                    try:
                        if hasattr(self.cur_state, 'enter'):
                            self.cur_state.enter(event)
                    except Exception:
                        pass
                    return
            except Exception:
                # 체크 함수 내부 에러 무시
                continue

    def change_state(self, new_state, event=None):
        """ 강제로 상태를 변경하는 메서드 """
        if self.cur_state and hasattr(self.cur_state, 'exit'):
            self.cur_state.exit(event)
        
        self.cur_state = new_state
        
        if self.cur_state and hasattr(self.cur_state, 'enter'):
            self.cur_state.enter(event)
