from MainClass import MainClass
from Include import *
from OsongStudio import OsongStudio
from Driver import Driver

import pygame

import os
import platform

print ('O Song Studio by Osong, Inc. (Version %s)' % OSONGSTUDIO_VERSION)

# 먼가 제대로 동작하게 하려고 만든 코드인데,, 별 쓸모는 없는 것 같다
#if platform.system() != "Darwin":
    #os.chdir('/home/pi/osongstudio')

print("   \\        ")
print("    \\       ")
print("     \\      ")
print("      X     ")
print("    /   \\   ")
print("  /      \\  ")
print(" /        \\ ")
print("/          \\")

try:
    pygame.init()

    # 오송스튜디오 부팅음
    Driver.play_sound('osongstudio', False)
    time.sleep(1.25)

    for i in ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C-2']:
        Driver.play_sound(i, False)
        time.sleep(.15)
        Driver.stop_sound()

    # LCD 초기화
    Driver.initialize_lcd()

    Driver.display_ex('O Song Studio {0x00}{0x01}', 1)
    Driver.display('<-Record  Play->', 2)

    # 메인 OsongStudio 객체 생성
    osongstudio = OsongStudio()

    # 이곳 콜백들은 모두 osongstudio 객체를 호출하고, 핵심 기능들은 모두 OsongStudio 클래스에서 구현된다
    # 버튼 1 (녹음 버튼) 이 눌렸을 때 실행될 함수
    def button1_callback(a):

        if a == True:
            Driver.beep_sound(0, 'C', False)
            run_after(lambda: Driver.beep_stop(0), 0.05)
            return

        if a == False:
            if osongstudio.mode == OsongStudio.MODE_NONE:
                osongstudio.record()
            elif osongstudio.mode == OsongStudio.MODE_RECORD:
                osongstudio.finish_record()
            elif osongstudio.mode == OsongStudio.MODE_DEVELOPER_INFO:
                osongstudio.go_main()
            elif osongstudio.mode == OsongStudio.MODE_FILENAME_SELECT:
                osongstudio.filename_next_ch()
            else:
                osongstudio.select_next()

    # 버튼 2 (재생 버튼) 이 눌렸을 때 실행될 함수
    def button2_callback(a):
        if a == True:
            Driver.beep_sound(0, 'C', False)
            run_after(lambda: Driver.beep_stop(0), 0.05)

        if a == False:
            if osongstudio.mode == OsongStudio.MODE_NONE:
                osongstudio.play()
            elif osongstudio.mode == OsongStudio.MODE_DEVELOPER_INFO:
                osongstudio.go_main()
            elif osongstudio.mode == OsongStudio.MODE_PLAY:
                osongstudio.select()
            elif osongstudio.mode == OsongStudio.MODE_FILENAME_SELECT:
                osongstudio.filename_next()

    # 버튼 1이 길게 눌렸을 때 실행될 함수
    def b1_long_callback():
        if osongstudio.mode == OsongStudio.MODE_NONE:
            osongstudio.developer_info()
        elif osongstudio.mode == OsongStudio.MODE_FILENAME_SELECT:
            osongstudio.save_file()
        elif osongstudio.mode == OsongStudio.MODE_PLAY:
            osongstudio.destroy_file_like_osong()

    # 버튼 2가 길게 눌렸을 때 실행될 함수.. 인데 버튼 2가 길게 눌리는 동작을 하나도 구현을 안 해서 쓸모없는 코드가 되어버렸다..
    def b2_long_callback():
        # print ('button2 long~~')
        return

    # 카메라 입력을 받았을 때 (특정 칸이 평소보다 어두워짐) 실행될 함수
    def cam_callback(a):

        if a == 0:
            osongstudio.release_gunban()
            return

        # 도부터 높은 미까지 총 10음
        for i in range(10):
            if a & (2**i):
                # print ('piano %d' % i)

                osongstudio.press_gunban(i)
                break
    
    # 일정 시간 (여기서는 5초) 동안 입력이 없을 때 실행될 함수
    def cancel_callback():
        if osongstudio.mode == OsongStudio.MODE_PLAY:
            osongstudio.cancel_play()
    
    # 건반 (XPad) 의 상태가 바뀔 때 실행될 함수
    # g가 -1이면 그 어떤 XPad도 인식되지 않는 상태이고, -2이면 XPad가 아닌 무언가가 인식되는 상태이다
    def gunban_change_callback(g):
        # print ('gunban type: %d' % g)

        if g == 0 or g == 1:
            osongstudio.main_str = '<-Record  Play->'

            Driver.beep_sound(0, 'C', False)
            run_after(lambda: Driver.beep_stop(0), 0.5)

        elif g == -1:
            osongstudio.main_str = ' Insert XPad...'

        elif g == -2:
            osongstudio.main_str = ' Unknown XPad..'

        # 지금 상태가 None (메인 화면) 상태라면 메인화면으로 다시 가는 걸 호출해서 화면을 새로고침한다!
        if osongstudio.mode == OsongStudio.MODE_NONE:
            osongstudio.go_main()

    # mainclass 객체 생성
    mainclass = MainClass(button1_callback, button2_callback, cam_callback, cancel_callback, 
        b1_long_callback, b2_long_callback, gunban_change_callback)

    # 메인 루프, 여기서 일정 시간마다 mainclass.tick() 를 호출한다
    while True:
        mainclass.tick()
        time.sleep(0.002)

finally:
    mainclass.destory_like_osong()
