# main.py
import sys
from gui.app import SimulatorApp

def main():
    print("멀티코어 스케줄링 시뮬레이터를 시작합니다.")
    
    # 2단계에서 정성들여 만든 GUI 메인 창(도화지와 패널)을 메모리에 올립니다.
    app = SimulatorApp()
    
    # 창을 화면에 띄우고, 사용자가 X 버튼을 눌러 종료할 때까지 대기합니다.
    app.mainloop()
    
    print("시뮬레이터가 종료되었습니다.")

if __name__ == "__main__":
    main()