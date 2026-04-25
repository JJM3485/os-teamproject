from scheduler.abstract_scheduler import AbstractScheduler

class RRScheduler(AbstractScheduler):
    #ready_queue에 먼저 도착한 프로세스를 빈 코어에 먼저 할당, 
    #time quantum이 지나면 선점하는 스케줄링

    #time_quantum, time 변수 추가
    def __init__(self, process_list, core_list, time_quantum):
        super().__init__(process_list, core_list)
        self.time_quantum = time_quantum

        #각 코어마다 현재 프로세스가 몇 초 실행됐는지 저장
        self.core_runtime = {core.core_id: 0 for core in self.cores}

    #ready_queue에 프로세스가 있으면 코어에 할당
    def _assign_process_to_core(self, core):
        if self.ready_queue:
            process = self.ready_queue.popleft()
            core.allocate(process)
            #프로세스 할당하면 core_runtime은 0
            self.core_runtime[core.core_id] = 0

    def do_schedule(self):
        #모든 코어 순회
        for core in self.cores:

            #빈 코어면 ready_queue에서 프로세스 할당
            if core.is_idle():
                self._assign_process_to_core(core)
            
            #time quantum 다 쓰면 선점
            elif self.core_runtime[core.core_id] >= self.time_quantum:
                preempted_process = core.force_eject()
                self.ready_queue.append(preempted_process)

                #다음 프로세스 할당
                self._assign_process_to_core(core)

        #실행 중인 코어들의 실행 시간 1증가
        for core in self.cores:
            if not core.is_idle():
                self.core_runtime[core.core_id] += 1

