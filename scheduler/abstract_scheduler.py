from collections import deque
from abc import ABC, abstractmethod
from core.system_components import Process, Core

class AbstractScheduler(ABC):
    #모든 스케줄러가 공통으로 상속받을 1초 단위 시뮬레이션 엔진
    def __init__(self, process_list: list[Process], core_list: list[Core]):
        self.incoming_queue = sorted(process_list, key=lambda x: x.at)
        self.cores = sorted(core_list, key=lambda x: x.core_id)
        
        self.ready_queue = deque()
        self.completed_processes = []
        self.clock = 0
        self.total_processes_count = len(process_list)

    def tick(self) -> bool:
        # 모든 프로세스의 처리가 끝났는지 종료 조건 검사
        if len(self.completed_processes) == self.total_processes_count:
            return False

        self._fetch_new_arrivals()
        self.do_schedule()              # 이걸로 오버라이딩 해야함
        self._run_cores_for_one_tick()
        self._increment_waiting_time()
        self.clock += 1
        
        return True

    def _fetch_new_arrivals(self):
        #현재 시간에 맞춰 도착한 프로세스를 Ready Queue로 넣기
        while self.incoming_queue and self.incoming_queue[0].at <= self.clock:
            self.ready_queue.append(self.incoming_queue.pop(0))

    @abstractmethod
    def do_schedule(self):
        #자식 클래스(스케줄링 알고리즘)에서 구현해야 하는 코어 할당 로직
        pass

    def _run_cores_for_one_tick(self):
        #모든 코어를 1초 작동하고 완료된 프로세스의 TT와 NTT 계산
        for core in self.cores:
            core.process_one_tick()
            
            if core.assigned_process and core.assigned_process.is_finished():
                finished_proc = core.force_eject()
                # 반환 시간(TT) = 끝난 시점(현재 clock + 1) - 도착 시간
                finished_proc.tt = (self.clock + 1) - finished_proc.at
                if finished_proc.bt > 0:
                    finished_proc.ntt = finished_proc.tt / finished_proc.bt
                self.completed_processes.append(finished_proc)

    def _increment_waiting_time(self):
        #Ready Queue에서 대기 중인 프로세스들의 대기 시간 1 증가
        for proc in self.ready_queue:
            proc.wt += 1