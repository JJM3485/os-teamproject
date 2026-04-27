from scheduler.abstract_scheduler import AbstractScheduler

class SPNScheduler(AbstractScheduler):
    # ready_queue에 있는 프로세스들 중 실행 시간이 가장 짧은 프로세스를
    # 빈 코어에 먼저 할당하는 비선점 스케줄링

    def do_schedule(self):
        # 모든 코어 순회
        for core in self.cores:

            # 빈 코어이고 ready_queue가 있는지 확인
            if core.is_idle() and self.ready_queue:

                # ready_queue 안에서 실행 시간이 가장 짧은 프로세스 찾기
                # 실행 시간이 같으면 먼저 도착한 프로세스를 우선 선택
                shortest_process = min(
                    self.ready_queue,
                    key=lambda p: (p.bt, p.at, p.p_id)
                )

                # 찾은 프로세스를 ready_queue에서 제거
                self.ready_queue.remove(shortest_process)

                # 빈 코어에 꺼내온 프로세스 할당
                core.allocate(shortest_process)