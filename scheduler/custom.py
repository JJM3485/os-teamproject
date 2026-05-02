from scheduler.abstract_scheduler import AbstractScheduler

class CustomScheduler(AbstractScheduler):

    def __init__(self, process_list, core_list, time_quantum=2, alpha=0.5):
        # 부모 클래스 초기화
        super().__init__(process_list, core_list)

        self.time_quantum = time_quantum
        self.alpha = alpha
        self.promotion_threshold = 2.0

        # 각 코어별 실행 시간 기록
        self.time_slice_used = {core.core_id: 0 for core in self.cores}
        
        self.p_ready_queue = []
        self.e_ready_queue = []
        self.ema_rt = 0.0

    def calculate_priority(self, process):
        # 우선순위 계산
        if process.rt == 0:
            return 0
        return (process.wt / process.rt) + (self.alpha * process.wt)

    def do_schedule(self):
        # 부모 클래스가 self.ready_queue에 넣어둔 새 프로세스들을 빼와서 분류
        while self.ready_queue:
            p = self.ready_queue.popleft() 
            
            if self.ema_rt == 0.0:
                self.ema_rt = p.rt
            else:
                self.ema_rt = (self.ema_rt * 0.8) + (p.rt * 0.2)

            # 평균보다 짧으면 P코어행 길면 E코어행
            if p.rt < self.ema_rt:
                self.p_ready_queue.append(p)
            else:
                self.e_ready_queue.append(p)


        # 선점 조건 체크 및 강제 선점 (Preemption)
        for core in self.cores:
            if not core.is_idle():
                # 코어 타입에 따라 TQ 한계치 다르게 적용 (P는 1배 E는 2배)
                limit = self.time_quantum if core.core_type == 'P' else self.time_quantum * 2
                
                if self.time_slice_used[core.core_id] >= limit:
                    process = core.force_eject()
                    self.time_slice_used[core.core_id] = 0
                    
                    # 방을 뺀 프로세스 재배치 
                    # 대기 시간이 길어 승격 조건을 만족하면 P코어 큐로
                    if self.calculate_priority(process) >= self.promotion_threshold:
                        self.p_ready_queue.append(process)
                    # 현재의 동적 평균값보다 짧으면 P코어 큐 길면 E코어 큐
                    elif process.rt < self.ema_rt:
                        self.p_ready_queue.append(process)
                    else:
                        self.e_ready_queue.append(process)

        # 승격 조건 확인
        promoted_processes = []
        for p in self.e_ready_queue:
            if self.calculate_priority(p) >= self.promotion_threshold:
                promoted_processes.append(p)

        # 승격 대상자들을 E큐에서 빼서 P큐로 이동
        for p in promoted_processes:
            self.e_ready_queue.remove(p)
            self.p_ready_queue.append(p)


        # P코어 할당 로직
        for core in [c for c in self.cores if c.core_type == 'P']:
            if core.is_idle() and self.p_ready_queue:
                best_process = max(
                    self.p_ready_queue,
                    key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                )
                self.p_ready_queue.remove(best_process)
                core.allocate(best_process)
                self.time_slice_used[core.core_id] = 0

        # E코어 할당 로직
        for core in [c for c in self.cores if c.core_type == 'E']:
            if core.is_idle() and self.e_ready_queue:
                best_process = max(
                    self.e_ready_queue,
                    key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                )
                self.e_ready_queue.remove(best_process)
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
        # 부모 클래스의 메서드 오버라이딩
        for proc in self.p_ready_queue:
            proc.wt += 1
        for proc in self.e_ready_queue:
            proc.wt += 1