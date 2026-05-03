from scheduler.abstract_scheduler import AbstractScheduler

class CustomScheduler(AbstractScheduler):

    def __init__(self, process_list, core_list, time_quantum=2, alpha=0.5):
        super().__init__(process_list, core_list)
        # 임계값 설정
        self.time_quantum = time_quantum
        self.alpha = alpha
        self.promotion_threshold = 15.0

        self.time_slice_used = {core.core_id: 0 for core in self.cores}
        
        self.p_ready_queue = []
        self.e_ready_queue = []
        
        self.total_arrived_bt = 0
        self.arrived_count = 0
        self.avg_bt = 0.0

    def calculate_priority(self, process):
        if process.rt == 0:
            return 0
        return (process.wt / process.rt) + (self.alpha * process.wt)

    def do_schedule(self):
        while self.ready_queue:
            p = self.ready_queue.popleft() 
            
            # 정확한 평균 실행 시간 실시간 계산
            self.total_arrived_bt += p.bt
            self.arrived_count += 1
            self.avg_bt = self.total_arrived_bt / self.arrived_count

            # 평균 이하면 P코어, 초과면 E코어로 배정
            if p.rt <= self.avg_bt:
                self.p_ready_queue.append(p)
            else:
                self.e_ready_queue.append(p)

        for core in self.cores:
            if not core.is_idle():
                limit = self.time_quantum if core.core_type == 'P' else self.time_quantum * 2
                
                if self.time_slice_used[core.core_id] >= limit:
                    process = core.force_eject()
                    self.time_slice_used[core.core_id] = 0

                    if self.calculate_priority(process) >= self.promotion_threshold:
                        self.p_ready_queue.append(process)
                    elif process.rt <= self.avg_bt:
                        self.p_ready_queue.append(process)
                    else:
                        self.e_ready_queue.append(process)

        promoted_processes = []
        for p in self.e_ready_queue:
            if self.calculate_priority(p) >= self.promotion_threshold:
                promoted_processes.append(p)

        for p in promoted_processes:
            self.e_ready_queue.remove(p)
            self.p_ready_queue.append(p)

        # P코어 할당 로직
        for core in [c for c in self.cores if c.core_type == 'P']:
            if core.is_idle():
                if self.p_ready_queue:
                    best_process = max(
                        self.p_ready_queue,
                        key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                    )
                    self.p_ready_queue.remove(best_process)
                    core.allocate(best_process)
                    self.time_slice_used[core.core_id] = 0
                elif self.e_ready_queue:
                    best_process = max(
                        self.e_ready_queue,
                        key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                    )
                    self.e_ready_queue.remove(best_process)
                    core.allocate(best_process)
                    self.time_slice_used[core.core_id] = 0

        # E코어 할당 로직 
        for core in [c for c in self.cores if c.core_type == 'E']:
            if core.is_idle():
                if self.e_ready_queue:
                    best_process = max(
                        self.e_ready_queue,
                        key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                    )
                    self.e_ready_queue.remove(best_process)
                    core.allocate(best_process)
                    self.time_slice_used[core.core_id] = 0
                elif self.p_ready_queue:
                    best_process = max(
                        self.p_ready_queue,
                        key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                    )
                    self.p_ready_queue.remove(best_process)
                    core.allocate(best_process)
                    self.time_slice_used[core.core_id] = 0

    def _run_cores_for_one_tick(self):
        for core in self.cores:
            if core.assigned_process is not None:
                self.time_slice_used[core.core_id] += 1
            else:
                self.time_slice_used[core.core_id] = 0

            core.process_one_tick()

            if core.assigned_process and core.assigned_process.is_finished():
                finished_proc = core.force_eject()
                finished_proc.tt = (self.clock + 1) - finished_proc.at
                
                if finished_proc.bt > 0:
                    finished_proc.ntt = finished_proc.tt / finished_proc.bt
                    
                self.completed_processes.append(finished_proc)
                self.time_slice_used[core.core_id] = 0

    def _increment_waiting_time(self):
        for proc in self.p_ready_queue:
            proc.wt += 1
        for proc in self.e_ready_queue:
            proc.wt += 1