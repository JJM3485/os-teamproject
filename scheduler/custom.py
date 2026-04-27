from scheduler.abstract_scheduler import AbstractScheduler

class CustomScheduler(AbstractScheduler):
    # 빈 코어에 먼저 할당하고, 일정 시간 이상 실행된 프로세스는 다시 ready_queue로 보내는 하이브리드 스케줄링

    def __init__(self, process_list, core_list, time_quantum=2, alpha=0.5):
        # 부모 클래스 초기화
        super().__init__(process_list, core_list)

        # 한 프로세스가 연속으로 사용할 수 있는 최대 시간
        self.time_quantum = time_quantum

        # 오래 기다린 프로세스의 우선순위를 얼마나 올릴지 정하는 값
        self.alpha = alpha

        # 각 코어별로 현재 프로세스가 몇 tick 실행되었는지 저장
        self.time_slice_used = {core.core_id: 0 for core in self.cores}

    def calculate_priority(self, process):
        # AFHS 우선순위 계산
        # 대기 시간이 길수록, 남은 실행 시간이 짧을수록 우선순위가 높아짐
        return (process.wt / process.rt) + (self.alpha * process.wt)

    def do_schedule(self):
        # 모든 코어 순회
        for core in self.cores:

            # 현재 코어에서 실행 중인 프로세스가 time quantum 이상 실행되었는지 확인
            if not core.is_idle() and self.time_slice_used[core.core_id] >= self.time_quantum:

                # 현재 실행 중인 프로세스를 코어에서 꺼내서 ready_queue로 다시 넣기
                process = core.force_eject()
                self.ready_queue.append(process)

                # 해당 코어의 실행 시간 기록 초기화
                self.time_slice_used[core.core_id] = 0

        # 모든 코어 순회
        for core in self.cores:

            # 빈 코어이고 ready_queue가 있는지 확인
            if core.is_idle() and self.ready_queue:

                # ready_queue 안에서 AFHS 우선순위가 가장 높은 프로세스 찾기
                # 우선순위가 같으면 남은 실행 시간이 더 짧은 프로세스를 우선 선택
                best_process = max(
                    self.ready_queue,
                    key=lambda p: (self.calculate_priority(p), -p.rt, -p.at, -p.p_id)
                )

                # 찾은 프로세스를 ready_queue에서 제거
                self.ready_queue.remove(best_process)

                # 빈 코어에 꺼내온 프로세스 할당
                core.allocate(best_process)

                # 새로 할당된 프로세스의 실행 시간 기록 초기화
                self.time_slice_used[core.core_id] = 0

    def _run_cores_for_one_tick(self):
        # 모든 코어를 1초씩 실행
        for core in self.cores:

            # 현재 코어에 프로세스가 있으면 실행 시간 1 증가
            if core.assigned_process is not None:
                self.time_slice_used[core.core_id] += 1
            else:
                self.time_slice_used[core.core_id] = 0

            # 코어를 1 tick 실행
            core.process_one_tick()

            # 실행이 끝난 프로세스가 있는지 확인
            if core.assigned_process and core.assigned_process.is_finished():

                # 종료된 프로세스를 코어에서 꺼내기
                finished_proc = core.force_eject()

                # 반환 시간 계산
                finished_proc.tt = (self.clock + 1) - finished_proc.at

                # 정규화 반환 시간 계산
                if finished_proc.bt > 0:
                    finished_proc.ntt = finished_proc.tt / finished_proc.bt

                # 완료된 프로세스 목록에 추가
                self.completed_processes.append(finished_proc)

                # 해당 코어의 실행 시간 기록 초기화
                self.time_slice_used[core.core_id] = 0