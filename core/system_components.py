class Process:
    # 프로세스 제어 블록
    def __init__(self, p_id: int, arrival_time: int, burst_time: int):
        self.p_id = p_id
        self.at = arrival_time
        self.bt = burst_time
        self.rt = burst_time  # 남은 실행 시간 
        self.wt = 0           # 대기 시간 
        self.tt = 0           # 반환 시간 
        self.ntt = 0.0        # 정규화 반환 시간

    def is_finished(self) -> bool:
        return self.rt <= 0


class Core:
    # P코어와 E코어의 특성을 구현
    def __init__(self, core_id: int, core_type: str):
        self.core_id = core_id
        self.core_type = core_type.upper()
        self.assigned_process: Process = None
        
        self.total_power_consumed = 0.0
        self.is_awake = False
        self.history = []  # 간트 차트 렌더링을 위한 초 단위 프로세스 점유 기록
        
        if self.core_type == 'P':
            self.boot_power = 0.5
            self.run_power = 3.0
            self.work_capacity = 2
        else:
            self.boot_power = 0.1
            self.run_power = 1.0
            self.work_capacity = 1

    def is_idle(self) -> bool:
        return self.assigned_process is None

    def allocate(self, process: Process):
        if not self.is_awake:
            self.is_awake = True
            self.total_power_consumed += self.boot_power
        self.assigned_process = process

    def force_eject(self) -> Process:
        ejected = self.assigned_process
        self.assigned_process = None
        return ejected

    def process_one_tick(self):
        if self.assigned_process is not None:
            self.history.append(self.assigned_process.p_id)
            
            # 남은 작업이 속도보다 작아도 1초치 전력을 전부 소모하도록 방어 로직 적용
            self.total_power_consumed += self.run_power
            self.assigned_process.rt = max(0, self.assigned_process.rt - self.work_capacity)
        else:
            self.history.append(None)
            self.is_awake = False  # 작업이 없으면 즉시 휴면 모드 전환