import tkinter as tk
from tkinter import ttk, messagebox

class InputPanel(ttk.Frame):
    def __init__(self, master, start_callback):
        super().__init__(master)
        self.start_callback = start_callback
        self.process_data = []  # 입력받은 프로세스 임시 저장
        self.core_data = []     # 입력받은 코어 임시 저장
        self.p_count = 1
        self.c_count = 1
        
        self._build_ui()

    def _build_ui(self):
        # 프로세스 추가 섹션
        ttk.Label(self, text="[프로세스 추가]", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        ttk.Label(self, text="도착 시간(AT):").grid(row=1, column=0, sticky="e")
        self.entry_at = ttk.Entry(self, width=8)
        self.entry_at.grid(row=1, column=1, pady=2)
        
        ttk.Label(self, text="실행 시간(BT):").grid(row=2, column=0, sticky="e")
        self.entry_bt = ttk.Entry(self, width=8)
        self.entry_bt.grid(row=2, column=1, pady=2)
        
        ttk.Button(self, text="프로세스 추가", command=self.add_process).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 코어 추가 섹션
        ttk.Label(self, text="[다중 코어 추가]", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=(15, 5))
        
        ttk.Label(self, text="코어 타입:").grid(row=5, column=0, sticky="e")
        self.core_var = tk.StringVar(value="P")
        ttk.Combobox(self, textvariable=self.core_var, values=["P", "E"], state="readonly", width=5).grid(row=5, column=1, pady=2)
        
        ttk.Button(self, text="코어 추가", command=self.add_core).grid(row=6, column=0, columnspan=2, pady=5)
        
        # 알고리즘 선택 및 시작 부분
        ttk.Label(self, text="[시뮬레이션 설정]", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=2, pady=(15, 5))
        
        ttk.Label(self, text="알고리즘:").grid(row=8, column=0, sticky="e")
        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_combo = ttk.Combobox(self, textvariable=self.algo_var, values=["FCFS", "RR", "SPN", "SRTN", "HRRN", "Custom"], state="readonly", width=10)
        self.algo_combo.grid(row=8, column=1, pady=2)
        
        # 콤보박스 값이 바뀔 때마다 함수 실행
        self.algo_combo.bind("<<ComboboxSelected>>", self.on_algo_change)
        
        # Label도 변수로 저장
        self.lbl_tq = ttk.Label(self, text="Time Quantum:")
        self.lbl_tq.grid(row=9, column=0, sticky="e")
        self.entry_tq = ttk.Entry(self, width=8)
        self.entry_tq.insert(0, "2")
        self.entry_tq.grid(row=9, column=1, pady=2)
        
        self.lbl_alpha = ttk.Label(self, text="Alpha (Custom):")
        self.lbl_alpha.grid(row=10, column=0, sticky="e")
        self.entry_alpha = ttk.Entry(self, width=8)
        self.entry_alpha.insert(0, "0.5")
        self.entry_alpha.grid(row=10, column=1, pady=2)

        ttk.Button(self, text="시뮬레이션 시작", command=self.start_sim).grid(row=11, column=0, columnspan=2, pady=10)

        # 현황판
        ttk.Label(self, text="[현재 추가된 항목]", font=("Arial", 10, "bold")).grid(row=12, column=0, columnspan=2, pady=(5, 5))
        
        list_frame = ttk.Frame(self)
        list_frame.grid(row=13, column=0, columnspan=2, sticky="nsew", padx=5)
        
        self.status_listbox = tk.Listbox(list_frame, height=10, width=25)
        self.status_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.status_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_listbox.config(yscrollcommand=scrollbar.set)

        # 프로그램이 켜졌을 때 초기 상태 세팅 
        self.on_algo_change()

    # 위젯 숨기기 및 보이기
    def on_algo_change(self, event=None):
        algo = self.algo_var.get()
        
        
        self.lbl_tq.grid_remove()
        self.entry_tq.grid_remove()
        self.lbl_alpha.grid_remove()
        self.entry_alpha.grid_remove()
        
       
        if algo == "RR":
            self.lbl_tq.grid()
            self.entry_tq.grid()
        elif algo == "Custom":
            self.lbl_tq.grid()      
            self.entry_tq.grid()
            self.lbl_alpha.grid()
            self.entry_alpha.grid()

    def add_process(self):
        if self.p_count > 15:
            messagebox.showwarning("경고", "프로세스는 최대 15개까지만 추가 가능합니다.")
            return
        try:
            at = int(self.entry_at.get())
            bt = int(self.entry_bt.get())
            self.process_data.append((self.p_count, at, bt))
            self.status_listbox.insert("end", f"P{self.p_count} (AT: {at}, BT: {bt})")
            self.p_count += 1
            self.entry_at.delete(0, 'end')
            self.entry_bt.delete(0, 'end')
            self.status_listbox.yview("end")
        except ValueError:
            messagebox.showerror("오류", "도착 시간과 실행 시간은 숫자만 입력해주세요.")

    def add_core(self):
        if self.c_count > 4:
            messagebox.showwarning("경고", "프로세서는 최대 4개까지만 추가 가능합니다.")
            return
        c_type = self.core_var.get()
        self.core_data.append((self.c_count, c_type))
        self.status_listbox.insert("end", f"Core {self.c_count} ({c_type} 타입)")
        self.c_count += 1
        self.status_listbox.yview("end")

    def start_sim(self):
        if not self.process_data or not self.core_data:
            messagebox.showwarning("경고", "프로세스와 코어를 최소 1개 이상 추가해주세요.")
            return
            
        algo = self.algo_var.get()
        # 입력창이 숨겨져 있을 때를 대비한 기본값 세팅
        tq_value = 2
        alpha_value = 0.5
        
        try:
            # RR이거나 custom일 때만 TQ를 읽어옴
            if algo in ["RR", "Custom"]:
                tq_value = int(self.entry_tq.get())
                if tq_value <= 0:
                    raise ValueError # 타임 퀀텀이 0 이하면 내보냄
            
            # custom일 때만 Alpha를 읽어옴
            if algo == "Custom":
                alpha_value = float(self.entry_alpha.get())
                
        except ValueError:
            messagebox.showerror("입력 오류", "Time Quantum은 1 이상의 정수, Alpha는 소수점 숫자여야 합니다.")
            return
            
        self.start_callback(self.process_data, self.core_data, algo, tq_value, alpha_value)