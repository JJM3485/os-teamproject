import tkinter as tk
from tkinter import ttk

class ResultVisualizer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # 위는 간트 차트를 그릴 캔버스
        self.canvas = tk.Canvas(self, bg="white", height=250)
        self.canvas.pack(fill="x", pady=5)
        
        # 아래는 결과표
        columns = ("PID", "AT", "BT", "WT", "TT", "NTT")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)
        
        # 소비 전력 표시 구역
        power_frame = ttk.Frame(self)
        power_frame.pack(side="right", padx=10, pady=5)

        # P코어 전력 라벨
        self.p_power_label = ttk.Label(power_frame, text="P-Core 총 전력: 0.00 W", font=("Arial", 10))
        self.p_power_label.pack(anchor="e")

        # E코어 전력 라벨
        self.e_power_label = ttk.Label(power_frame, text="E-Core 총 전력: 0.00 W", font=("Arial", 10))
        self.e_power_label.pack(anchor="e")

        # 시스템 전체 전력 라벨
        self.total_power_label = ttk.Label(power_frame, text="시스템 합계: 0.00 W", font=("Arial", 11, "bold"), foreground="blue")
        self.total_power_label.pack(anchor="e", pady=(5, 0))

        time_frame = ttk.Frame(self)
        time_frame.pack(side="right", padx=30, pady=5) # padx로 전력 텍스트와 간격 벌림

        self.total_time_label = ttk.Label(time_frame, text="총 소요 시간: 0 초", font=("Arial", 12, "bold"), foreground="green")
        self.total_time_label.pack(anchor="e", pady=(0, 5))

    def draw_gantt(self, cores):
        # 매 초마다 코어 기록을 읽어와 갱신
        self.canvas.delete("all")
        colors = ["#FF9999", "#99CCFF", "#99FF99", "#FFCC99", "#CC99FF", "#FFFF99"]
        
        block_width = 30
        block_height = 30
        y_offset = 20

        for idx, core in enumerate(cores):
            y1 = y_offset + (idx * (block_height + 15))
            y2 = y1 + block_height
            # 코어 이름 출력
            self.canvas.create_text(40, y1 + 15, text=f"Core {core.core_id}({core.core_type})", font=("Arial", 9, "bold"))
            
            # 시간에 따른 프로세스 점유 기록 블록 그리기
            for time_tick, pid in enumerate(core.history):
                x1 = 80 + (time_tick * block_width)
                x2 = x1 + block_width
                if pid is not None:
                    color = colors[pid % len(colors)]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                    self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=f"P{pid}")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#EEEEEE", outline="gray") # 빈 코어 (휴면)

    def update_result(self, completed_procs, cores):
        # 시뮬레이션 종료 시 결과 표와 전력을 업데이트
        # 기존 표 데이터 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 프로세스 결과 채우기
        completed_procs.sort(key=lambda x: x.p_id) # PID 순서로 정렬
        for p in completed_procs:
            self.tree.insert("", "end", values=(f"P{p.p_id}", p.at, p.bt, p.wt, p.tt, f"{p.ntt:.2f}"))
            
        if completed_procs:
            # (도착 시간 + 반환 시간) 중 가장 큰 값이 최종 종료 시간
            total_time = max(p.at + p.tt for p in completed_procs)
        else:
            total_time = 0
            
        self.total_time_label.config(text=f"총 소요 시간: {total_time} 초")
        
        # 전력 계산
        p_power = sum(c.total_power_consumed for c in cores if c.core_type == 'P')
        e_power = sum(c.total_power_consumed for c in cores if c.core_type == 'E')
        total_sum = p_power + e_power
        
        self.p_power_label.config(text=f"P-Core 총 전력: {p_power:.2f} W")
        self.e_power_label.config(text=f"E-Core 총 전력: {e_power:.2f} W")
        self.total_power_label.config(text=f"시스템 합계: {total_sum:.2f} W")