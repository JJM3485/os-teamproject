from scheduler.abstract_scheduler import AbstractScheduler

class FCFSScheduler(AbstractScheduler):
    #ready_queue에 먼저 도착한 프로세스를 빈 코어에 먼저 할당하는 비선점 스케줄링

    def do_schedule(self):
        #모든 코어 순회
        for core in self.cores:

            #빈 코어이고 ready_queue가 있는지 확인
            if core.is_idle() and self.ready_queue:

                #ready_queue 맨 앞에 있는 프로세스 꺼내기
                process = self.ready_queue.popleft()
                
                #빈 코어에 꺼내온 프로세스 할당
                core.allocate(process)
      