from scheduler.abstract_scheduler import AbstractScheduler

class SRTNScheduler(AbstractScheduler):
    def do_schedule(self):
        # 빈 코어가 있다면 우선 남은 시간이 가장 짧은 프로세스를 채워 넣음
        for core in self.cores:
            if core.is_idle() and self.ready_queue:
                shortest_process = min(self.ready_queue, key=lambda p: p.rt)
                self.ready_queue.remove(shortest_process)
                core.allocate(shortest_process)

        # 선점 로직
        if self.ready_queue:
            for core in self.cores:
                if not core.is_idle():
                    # 큐에 대기 중인 애들 중 가장 남은 시간이 짧은 프로세스
                    shortest_in_queue = min(self.ready_queue, key=lambda p: p.rt)
                    
                    
                    if shortest_in_queue.rt < core.assigned_process.rt:
                        # 돌고 있던 애를 쫓아내서 큐에 다시 넣음
                        preempted_process = core.force_eject()
                        self.ready_queue.append(preempted_process)
                        
                        # 큐에 있던 짧은 애를 코어에 새로 할당
                        self.ready_queue.remove(shortest_in_queue)
                        core.allocate(shortest_in_queue)