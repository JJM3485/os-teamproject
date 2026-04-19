from scheduler.abstract_scheduler import AbstractScheduler

class HRRNScheduler(AbstractScheduler):
    def do_schedule(self):
        # 모든 코어를 순회하며 빈 코어 참색
        for core in self.cores:
            
            # 코어가 비어있고 레디 큐에 대기 중인 프로세스가 있는지 확인
            if core.is_idle() and self.ready_queue:
                
                # 레디 큐 안의 모든 프로세스들의 응답 비율을 계산하여 최고값 탐색
                best_process = max(
                    self.ready_queue, 
                    key=lambda p: (p.wt + p.bt) / p.bt if p.bt > 0 else 0
                )
                
                # 가장 비율이 높은 프로세스 가져오기
                self.ready_queue.remove(best_process)
                
                # 빈 코어에 해당 프로세스를 할당
                core.allocate(best_process)
                