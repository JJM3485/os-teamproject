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
        ttk.Label(self, text="[ 프로세스 추가 ]", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        ttk.Label(self, text="도착 시간(AT):").grid(row=1, column=0, sticky="e")
        self.entry_at = ttk.Entry(self, width=8)
        self.entry_at.grid(row=1, column=1, pady=2)
        
        ttk.Label(self, text="실행 시간(BT):").grid(row=2, column=0, sticky="e")
        self.entry_bt = ttk.Entry(self, width=8)
        self.entry_bt.grid(row=2, column=1, pady=2)
        
        ttk.Button(self, text="프로세스 추가", command=self.add_process).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 코어 추가 섹션
        ttk.Label(self, text="[ 다중 코어 추가 ]", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=(15, 5))
        
        ttk.Label(self, text="코어 타입:").grid(row=5, column=0, sticky="e")
        self.core_var = tk.StringVar(value="P")
        ttk.Combobox(self, textvariable=self.core_var, values=["P", "E"], state="readonly", width=5).grid(row=5, column=1, pady=2)
        
        ttk.Button(self, text="코어 추가", command=self.add_core).grid(row=6, column=0, columnspan=2, pady=5)
        
        # 알고리즘 선택 및 시작 섹션
        ttk.Label(self, text="[ 시뮬레이션 설정 ]", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=2, pady=(15, 5))
        
        ttk.Label(self, text="알고리즘:").grid(row=8, column=0, sticky="e")
        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_combo = ttk.Combobox(self, textvariable=self.algo_var, values=["FCFS", "RR", "SPN", "SRTN", "HRRN", "Custom"], state="readonly", width=10)
        self.algo_combo.grid(row=8, column=1, pady=2)
        
        # 타임 퀀텀
        ttk.Label(self, text="Time Quantum:").grid(row=9, column=0, sticky="e")
        self.entry_tq = ttk.Entry(self, width=8)
        self.entry_tq.insert(0, "2")
        self.entry_tq.grid(row=9, column=1, pady=2)
        
        ttk.Button(self, text="▶ 시뮬레이션 시작", command=self.start_sim).grid(row=10, column=0, columnspan=2, pady=10)

        # 현황판
        ttk.Label(self, text="[ 현재 추가된 항목 ]", font=("Arial", 10, "bold")).grid(row=11, column=0, columnspan=2, pady=(5, 5))
        
        list_frame = ttk.Frame(self)
        list_frame.grid(row=12, column=0, columnspan=2, sticky="nsew", padx=5)
        
        self.status_listbox = tk.Listbox(list_frame, height=10, width=25)
        self.status_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.status_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_listbox.config(yscrollcommand=scrollbar.set)

    def add_process(self):
        if self.p_count > 15:
            messagebox.showwarning("경고", "프로세스는 최대 15개까지만 추가 가능합니다.")
            return
        try:
            at = int(self.entry_at.get())
            bt = int(self.entry_bt.get())
            self.process_data.append((self.p_count, at, bt))
  
            self.status_listbox.insert("end", f" P{self.p_count} (AT: {at}, BT: {bt})")
            
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
        # app.py에 있는 start_simulation 함수를 호출해 데이터 전달
        self.start_callback(self.process_data, self.core_data, self.algo_var.get())