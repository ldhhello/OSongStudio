from Include import *
from Driver import Driver
from ProgressBar import ProgressBar
import os
from OSONGOSS import OsongOSS

# OsongStudio의 핵심 기능들을 담당하는 클래스
# OsongStudio의 모든 기능들은 여기서 처리되고, 하드웨어 입/출력은 모두 추상화된 입/출력을 이용한다
class OsongStudio:

    MODE_NONE = 0 # 메인 화면
    MODE_RECORD = 1 # 녹음 중인 상태
    MODE_PLAY = 2 # 재생 중인 상태
    MODE_DEVELOPER_INFO = 3 # 개발자 정보 화면
    MODE_FILENAME_SELECT = 4 # 저장할 파일 이름 만드는 화면
    MODE_PREPARE = 5 # 무언가 하기 위해 준비중인 상태 (아무것도 하지 않는 상태)
    MODE_PLAYING = 6 # 플레이를 하고 있는 상태

    main_str = '<-Record  Play->'

    #file_list = ['DYNAMICOSONG', 'CRYINGIPHONE', 'HAPPYKANE', 'SADUMJUNSICK']
    file_list = []
    file_idx = 0

    progressbar = ProgressBar()

    def __init__(self):
        self.mode = OsongStudio.MODE_NONE
        print ('New OsongStudio Created!')

    # 녹음 시작 함수
    def record(self):
        self.osongoss.initialize()
        self.mode = OsongStudio.MODE_RECORD

        self.last_gunban = -1
        self.last_pressed_time = -1
        self.last_octave = -1

        Driver.display('', 2)
        Driver.display('  Recording...  ', 2)

    last_gunban = -1
    last_pressed_time = -1
    last_octave = -1

    # 녹음이 끝났을 때 실행될 함수
    def finish_record(self):
        current = time.time()

        if self.last_gunban != -1:
            self.osongoss.append(self.sound_name[self.last_gunban], current - self.last_pressed_time, self.last_octave)

        Driver.display('', 2)
        Driver.display('Recording Finish', 2)

        run_after(lambda: self.start_filename_select(), 2)
    
    # 저장할 파일 이름 만드는 함수
    filename_str = ''
    now_ch = 65
    def start_filename_select(self):
        self.mode = OsongStudio.MODE_FILENAME_SELECT

        Driver.display('Filename to save', 1)
        self.filename_str = ''
        self.now_ch = 65
        Driver.display('', 2)
        # 0x7e : ->
        Driver.display_ex(' {0x7E} %s%s' % (self.filename_str, chr(self.now_ch)), 2)

    # 파일 이름 만들기 때, 현재 문자를 다음 문자로(A이면 B로, B면 C로, ...) 바꾸는 함수
    def filename_next_ch(self):
        self.now_ch += 1
        if self.now_ch > ord('Z'):
            self.now_ch = 65

        Driver.display_ex(' {0x7E} %s%s' % (self.filename_str, chr(self.now_ch)), 2)
    
    # 파일 이름 만들기 때, 다음 글자로 넘어가는 (ABC 이면 ABCA로, ...) 바꾸는 함수
    def filename_next(self):
        self.filename_str += chr(self.now_ch)
        self.now_ch = 65

        if len(self.filename_str) == 13:
            self.save_file()

            return

        Driver.display_ex(' {0x7E} %s%s' % (self.filename_str, chr(self.now_ch)), 2)

    # 파일 저장하는 함수
    def save_file(self):
        self.filename_str += chr(self.now_ch)

        if not self.osongoss.write_file('%s/%s.osongoss' % (MUSIC_DIR, self.filename_str)):
            Driver.display('  File exists', 1)

            run_after(lambda: self.start_filename_select(), 2)

            return

        Driver.display('   File Saved   ', 1)

        self.mode = OsongStudio.MODE_PREPARE
        run_after(lambda: self.go_main(), 2)

    # 재생할 파일을 선택하는 함수
    def play(self):
        self.mode = OsongStudio.MODE_PLAY

        # ./Music/ 폴더를 읽어서 .osongoss(확장자) 를 빼서 화면에 출력되게 한다
        self.file_list = os.listdir(MUSIC_DIR)
        for idx, f in enumerate(self.file_list):
            self.file_list[idx] = f.replace('.osongoss', '')

        Driver.display(' Select file... ', 1)

        self.file_idx = 0

        Driver.display('#%d %s' % (self.file_idx+1, self.file_list[self.file_idx]), 2)

    # 재생할 파일 선택하는 화면에서 5초 동안 아무 입력이 없으면 원래 화면으로 돌아가는 함수
    def cancel_play(self):
        self.mode = OsongStudio.MODE_NONE

        self.clear_screen_after(0)

    # 재생할 파일 선택하는 화면에서 현재 커서를 다음으로 넘기는 함수 (#1 OSONG --> #2 SALBYEOL 이런식으로..)
    def select_next(self):
        self.file_idx += 1
        if self.file_idx >= len(self.file_list):
            self.file_idx = 0
        
        Driver.display('', 2)
        Driver.display('#%d %s' % (self.file_idx+1, self.file_list[self.file_idx]), 2)

    # 파일을 지우는 함수
    def destroy_file_like_osong(self):
        filename = self.file_list[self.file_idx]

        os.system('rm Music/%s.osongoss' % filename)
        
        Driver.display('  File erased', 1)
        
        self.clear_screen_after(2)

    progress_idx = 0
    osongoss = OsongOSS()
    start_time = 0

    # 재생할 파일이 선택됐을 때 호출되는 함수
    # 여기서 파일을 읽어서 재생을 시작한다!
    def select(self):
        Driver.display('  Selected #%d' % (self.file_idx+1), 1)

        self.mode = OsongStudio.MODE_PLAYING
        self.progress_idx = 0

        #self.osongoss = OsongOSS()
        self.osongoss.open_file('Music/%s.osongoss' % self.file_list[self.file_idx])

        self.progressbar.enable(True, 0, self.osongoss.song_length(), self.file_list[self.file_idx])

        self.start_time = time.time()
        run_after(lambda: self.progressbar_next(), 0.1)

        score = self.osongoss.next_()

        Driver.play_sound(score['score'], score['octave'])
        run_after(self.play_next, score['length'])
    
    # 다음 음을 스피커로 출력하는 함수
    def play_next(self):
        score = self.osongoss.next_()

        if score['score'] == -3000:
            return

        Driver.play_sound(score['score'], score['octave'])
        run_after(self.play_next, score['length'])

    # 프로그레스 바를 다음 위치로 넘기는 함수
    def progressbar_next(self):
        self.progress_idx = time.time() - self.start_time

        if self.progress_idx > self.osongoss.song_length():
            self.progressbar.disable()
            self.clear_screen_after(1)

            #self.mode = OsongStudio.MODE_NONE
            return
        
        self.progressbar.change_value(self.progress_idx)

        run_after(lambda: self.progressbar_next(), 0.1)

    # t초 후에 메인 화면으로 돌아가는 함수
    # t가 0이면 바로 메인 화면으로 돌아간다!
    def clear_screen_after(self, t):

        if t == 0:
            self.mode = OsongStudio.MODE_NONE

            Driver.change_character(Driver.CUSTOMCHARACTER_DEFAULT)
            Driver.display_ex('O Song Studio {0x00}{0x01}', 1)
            Driver.display(self.main_str, 2)

            return

        run_after(lambda: self.clear_screen_after(0), t)
    
    sound_name = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D', 'E']

    # 건반을 눌렀을 때 실행되는 함수
    # 스피커로 소리를 재생하고, 녹음 모드라면 녹음도 한다!
    def press_gunban(self, a):

        if self.mode == OsongStudio.MODE_PLAYING:
            return
        if self.mode == OsongStudio.MODE_FILENAME_SELECT:
            return

        octave = False
        if a >= 7:
            octave = True

        #Driver.beep_sound(0, self.sound_name[a], octave)
        Driver.play_sound(self.sound_name[a], octave)

        if self.mode != OsongStudio.MODE_RECORD:
            return

        current = time.time()

        if self.last_gunban != -1:
            self.osongoss.append(self.sound_name[self.last_gunban], current - self.last_pressed_time, self.last_octave)

        self.last_gunban = a
        self.last_pressed_time = current
        self.last_octave = octave

    # 건반을 뗐을 때 실행되는 함수
    def release_gunban(self):
        #Driver.beep_stop(0)
        Driver.stop_sound()

    # 개발자 정보!!
    def developer_info(self):
        self.mode = OsongStudio.MODE_DEVELOPER_INFO

        Driver.display('', 1)
        Driver.display_ex('{0x00}{0x01}{0x02}{0x03}{0x04}{0x00} v%s {0x05}' % OSONGSTUDIO_VERSION, 1) # 오송스튜디오 v1.0X X
        Driver.display('Made by LDH, JHU', 2)

    # 메인으로 돌아가는 함수,,
    def go_main(self):
        self.mode = OsongStudio.MODE_NONE

        self.clear_screen_after(0)