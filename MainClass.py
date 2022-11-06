from cmath import inf
from Driver import Driver
import time
from Include import *

# 들어오는 입력을 asynchronous 하게 처리할수 있게 해줌 (callback으로)
# 매 틱(단위 시간) 마다 하드웨어 입력을 검사하고, 알맞은 함수를 호출해줌
class MainClass:

    # GPIO map
    button1 = 17
    button2 = 18
    buzzer1 = 27

    last_b1 = False
    last_b2 = False
    last_cam = 0
    last_gunban = -1

    # 버튼 길게 누르기 관련
    b1_start = inf
    b2_start = inf
    ignore_b1 = False
    ignore_b2 = False

    last_input = inf

    def __init__(self, b1_callback, b2_callback, cam_callback, cancel_callback, b1_long_callback, b2_long_callback, gunban_callback):
        print ('MainClass created!')

        Driver.initialize([self.button1, self.button2], [self.buzzer1])

        self.button1_callback = b1_callback
        self.button2_callback = b2_callback
        self.camera_callback = cam_callback
        self.cancel_callback = cancel_callback
        self.b1_long_callback = b1_long_callback
        self.b2_long_callback = b2_long_callback
        self.gunban_change_callback = gunban_callback

    # 프로그램이 종료될때 호출됨
    def destory_like_osong(self):
        Driver.cleanup()

    # 매 틱(단위 시간) 마다 동작하는 코드
    def tick(self):

        current = time.time()

        b1 = self.get_button1()
        b2 = self.get_button2()

        b1_input = False

        if b1 == 0:
            b1 = False
        elif b1 == 1:
            b1 = True

        if b2 == 0:
            b2 = False
        elif b2 == 1:
            b2 = True

        # 버튼 1 입력 / 길게 입력 처리하는 코드
        if self.last_b1 is False and b1 is True:
            self.last_b1 = True
            self.b1_start = current
            b1_input = True
            self.last_input = current
        elif self.last_b1 is True and b1 is False:
            self.last_b1 = False
            self.b1_start = inf
            b1_input = True
            self.last_input = current
        
        if self.b1_start is not inf and current - self.b1_start >= 2:
            self.b1_start = inf
            self.ignore_b1 = True

            self.b1_long_callback()
        elif self.ignore_b1 is True and b1_input:
            self.ignore_b1 = False
        elif b1_input:
            
            self.button1_callback(b1)

        # 버튼 2 입력 / 길게 입력 처리하는 코드
        b2_input = False
        if self.last_b2 is False and b2 is True:
            self.last_b2 = True
            self.b2_start = current
            b2_input = True
            self.last_input = current
        elif self.last_b2 is True and b2 is False:
            self.last_b2 = False
            self.b2_start = inf
            b2_input = True
            self.last_input = current
        
        if self.b2_start is not inf and current - self.b2_start >= 2:
            self.b2_start = inf
            self.ignore_b2 = True

            self.b2_long_callback()
        elif self.ignore_b2 is True and b2_input:
            self.ignore_b2 = False
        elif b2_input:
            self.button2_callback(b2)

        # 카메라(무슨 음 눌렀는지) / 건반(XPad 타입) 처리하는 코드
        cam = self.get_camera()
        gunban = self.get_gunban()

        if self.last_cam != cam:
            self.last_cam = cam
            self.camera_callback(cam)
        if self.last_gunban != gunban:
            self.last_gunban = gunban
            self.gunban_change_callback(gunban)

        # run_after (Include.py) 에서 호출 예약해놓은 함수 호출하는 코드
        del_list = []
        for key in next_queue:
            if current >= key:
                del_list.append(key)

        for key in del_list:
            next_queue[key]()
            del next_queue[key]
        
        # 버튼 일정 시간동안 안 누르면 호출하는 코드
        if current - self.last_input >= 5:
            self.last_input = inf
            self.cancel_callback()

    # button1, button2 얘네는 눌렸는지/안눌렸는지로 false, true 리턴하고
    # 카메라는 카메라 처리 다 해서 어디가 눌렸는지 보고 1 ~ 2^(n+1) - 1 를 리턴한다
    # 리턴값이 a라고 하면 a & 2^k 가 0 이 아니라면 k번 건반이 눌린것으로 처리
    def get_button1(self):
        return Driver.get_button(self.button1)
    
    def get_button2(self):
        return Driver.get_button(self.button2)

    def get_camera(self):
        return Driver.get_camera()

    def get_gunban(self):
        return Driver.get_gunban_type()
