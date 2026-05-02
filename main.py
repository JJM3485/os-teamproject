# main.py
import sys
from gui.app import SimulatorApp

def main():
    print("멀티코어 스케줄링 시뮬레이터를 시작합니다.")
    
    app = SimulatorApp()
    app.mainloop()
    
    print("시뮬레이터가 종료되었습니다.")

if __name__ == "__main__":
    main()