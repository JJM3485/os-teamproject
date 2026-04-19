import tkinter as tk
from gui.components import InputPanel
from gui.visualizer import ResultVisualizer
from core.system_components import Process, Core
from scheduler.hrrn import HRRNScheduler
from scheduler.fcfs import FCFSScheduler
from scheduler.rr import RRScheduler
from scheduler.spn import SPNScheduler
from scheduler.srtn import SRTNScheduler
from scheduler.custom import CustomScheduler

class SimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("멀티코어 프로세스 스케줄링 시뮬레이터")
        self.geometry("900x600")
        
        # 좌측: 입력 패널
        self.input_panel = InputPanel(self, self.start_simulation)
        self.input_panel.pack(side="left", fill="y", padx=10, pady=10)
        
        # 우측: 결과 시각화 패널
        self.visualizer = ResultVisualizer(self)
        self.visualizer.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.scheduler = None

    def start_simulation(self, process_data, core_data, algo_name, tq):
        # 시작 버튼을 눌렀을 때 1회 호출
        # 입력 데이터를 실제 객체로 변환
        processes = [Process(pid, at, bt) for pid, at, bt in process_data]
        cores = [Core(cid, ctype) for cid, ctype in core_data]
        
        # 알고리즘 선택
        # 나중에 여기에 if algo_name == "FCFS": self.scheduler = FCFSScheduler(processes, cores) 형태로 연결
        if algo_name == "FCFS":
            self.scheduler = FCFSScheduler(processes, cores)
        elif algo_name == "RR":
            self.scheduler = RRScheduler(processes, cores, time_quantum=tq)
        elif algo_name == "SPN":
            self.scheduler = SPNScheduler(processes, cores)
        elif algo_name == "SRTN":
            self.scheduler = SRTNScheduler(processes, cores)
        elif algo_name == "HRRN":
            self.scheduler = HRRNScheduler(processes, cores)
        elif algo_name == "Custom":
            self.scheduler = CustomScheduler(processes, cores)
        
        if self.scheduler:
            self.run_step() # 엔진 가동 시작
        else:
            print(f"[{algo_name}] 알고리즘이 아직 연결되지 않았습니다. 팀원들이 코드를 짜오면 app.py에 연결하세요.")

    def run_step(self):
        # 0.2초마다 실제로 1Tick씩 움직이며 간트 차트를 그리는 무한 루프
        if self.scheduler and self.scheduler.tick():
            # 엔진이 1초 진행되었으므로 간트 차트를 그림
            self.visualizer.draw_gantt(self.scheduler.cores)
            
            # 0.2초뒤에 자기 자신을 다시 호출하여 루프를 돈다
            self.after(200, self.run_step) 
        else:
            # 엔진 가동이 종료되면 결과 표를 업데이트함
            if self.scheduler:
                self.visualizer.draw_gantt(self.scheduler.cores) 
                self.visualizer.update_result(self.scheduler.completed_processes, self.scheduler.cores)