import RPi.GPIO as GPIO
import cv2
from lcd import drivers
import platform
from CustomCharacter import CustomCharacter
import pygame
import time

# GPIO, 카메라, LCD 등등과 직접 통신하는 클래스
# 모든 하드웨어 입/출력은 이곳에서 처리된다
class Driver:

    pwm_list = []
    lcd = drivers.Lcd()

    CUSTOMCHARACTER_DEFAULT = 1
    CUSTOMCHARACTER_PROGRESSBAR = 2

    sound = {
        'C': 261, 'B#': 261,
        'C#': 277, 'Db': 277,
        'D': 294,
        'D#': 311, 'Eb': 311,
        'E': 330, 'Fb': 330,
        'F': 349, 'E#': 349,
        'F#': 370, 'Gb': 370,
        'G': 392,
        'G#': 415, 'Ab': 415,
        'A': 440,
        'A#': 466, 'Bb': 466,
        'B': 494, 'Cb': 494,
        'C-2': 261*2,
        'D-2': 294*2,
        'E-2': 330*2
    }

    @staticmethod
    def initialize(gpio_list, pwm_list):
        GPIO.setmode(GPIO.BCM)
        
        for pin in gpio_list:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        for pin in pwm_list:
            GPIO.setup(pin, GPIO.OUT)

            Driver.pwm_list.append(GPIO.PWM(pin, 220))
            Driver.pwm_list[-1].start(0) # -1: last index

        Driver.cap = cv2.VideoCapture(0)

        if not Driver.cap.isOpened():
            print ('No osong,,,')
            return 0

    @staticmethod
    def initialize_lcd():
        cc = CustomCharacter.default_character(Driver.lcd)
        cc.load_custom_characters_data()

    @staticmethod
    def change_character(type):
        if type == Driver.CUSTOMCHARACTER_DEFAULT:
            cc = CustomCharacter.default_character(Driver.lcd)
            cc.load_custom_characters_data()
        elif type == Driver.CUSTOMCHARACTER_PROGRESSBAR:
            cc = CustomCharacter.progressbar_character(Driver.lcd)
            cc.load_custom_characters_data()

    @staticmethod
    def get_button(gpio_pin):
        inp = GPIO.input(gpio_pin)
        return inp

    gunban_type = -1 # -1 : 없음, -2: 둘다 잡힘

    @staticmethod
    def get_camera():
        ret, frame = Driver.cap.read()
        if not ret:
            # print ('no osong,,,,')
            return 0

        # 플랫폼에 따라 좌우반전만 시킬지, 상하반전도 시킬지 결정
        # 라즈베리파이 실제 환경 (Raspberry Pi OS, Linux)에서는 상하, 좌우 모두 반전해야 현실 모습이 나온다 (카메라 배치 때문에..)
        # 근데 개발 환경 (macOS, Darwin)에서는 좌우만 반전해야 거울모드처럼 나온다!
        frame = cv2.flip(frame, 1)
        if platform.system() == "Darwin":
            frame = cv2.resize(frame[0:, 240:-240], (640, 480)) # 개발할때도 640x480으로 나오게
            #frame = cv2.imread('osong.png') # test
            #frame = cv2.resize(frame, (640, 480))
        else:
            frame = cv2.flip(frame, 0)

        # type_segment 가 첫번째꺼가 인식되는지, 두번째꺼가 인식되는지로 앞면, 뒷면을 처리한다
        type_segment = [
            [55, 60, 105, 95],
            [640-105, 60, 640-55, 95]
        ]

        # XPad 앞면, 뒷면에 따라 처리하는 코드.. 였는데
        # XPad 뒷면을 만들지 못해서 segment_list_2는 사실상 필요 없는 코드
        # [x1, y1, x2, y2]
        segment_list_1 = [
            [50, 410, 90, 470],
            [108, 410, 148, 470],
            [165, 410, 205, 470],
            [223, 410, 263, 470],
            [279, 410, 319, 470],
            [335, 410, 375, 470],
            [392, 410, 432, 470],
            [449, 410, 489, 470],
            [506, 410, 546, 470],
            [563, 410, 603, 470]
        ]
        segment_list_2 = [
            [100, 230, 170, 300],
            [200, 250, 270, 320],
            [300, 230, 370, 300],
            [400, 250, 470, 320],
            [500, 230, 570, 300]
        ]

        seg_idx = 0
        is_insik = False

        Driver.gunban_type = -1

        # XPad 앞면인지 뒷면인지, 아무것도 인식 안 되는지 판단하는 코드
        for seg in type_segment:

            image_crop = frame[seg[1]: seg[3], seg[0]: seg[2]]
            cv2.rectangle(frame, (seg[0], seg[1]), (seg[2], seg[3]), (255, 0, 0))

            avg_color = image_crop.mean(axis=(0,1))

            frame[seg[1]:seg[1]+10, seg[0]:seg[0]+10] = avg_color

            avg_color_avg = (avg_color[0] + avg_color[1] + avg_color[2]) / 3
            if avg_color_avg <= 50:
                if is_insik:
                    Driver.gunban_type = -2
                    break

                is_insik = True

                if Driver.gunban_type != seg_idx:
                    Driver.gunban_type = seg_idx

            seg_idx += 1

        if Driver.gunban_type == 0:
            segment_list = segment_list_1
        elif Driver.gunban_type == 1:
            segment_list = segment_list_2
        else:
            segment_list = []

        # 인식된 XPad에 따라 무슨 건반을 눌렀는지 인식하는 코드
        res = 0
        idx = 0
        for seg in segment_list:

            image_crop = frame[seg[1]: seg[3], seg[0]+10: seg[2]-10]
            cv2.rectangle(frame, (seg[0]+10, seg[1]), (seg[2]-10, seg[3]), (0, 255, 0))

            avg_color = image_crop.mean(axis=(0,1))

            frame[seg[1]:seg[1]+5, seg[0]+10:seg[0]+15] = avg_color

            avg_color_avg = (avg_color[0] + avg_color[1] + avg_color[2]) / 3
            if avg_color_avg <= 100:
                res |= 2**idx

            idx += 1

        # 디버그용 코드 (화면 출력,,)
        #cv2.imshow('frame', frame)
        #cv2.waitKey(2)
            
        return res

    # 비프음 내는 코드,,
    @staticmethod
    def beep(idx, freq):
        # print ('beep freq:%d' % freq)

        Driver.pwm_list[idx].ChangeFrequency(freq)
        Driver.pwm_list[idx].ChangeDutyCycle(50)
    
    # 파이썬 오버로딩 왜 안됨?~??~!?!~?~~!!?~!?~!?~?~~~@~!@!~~!~!@~?~?~@?~?₩/~12
    @staticmethod
    def beep_sound(idx, sound, octave):
        # print ('beep sound:%s' % sound)

        Hz = Driver.sound[sound]

        if octave:
            Hz *= 2

        Driver.pwm_list[idx].ChangeFrequency(Hz)
        Driver.pwm_list[idx].ChangeDutyCycle(50)

    @staticmethod
    def beep_stop(idx):
        # print ('beep stopped')

        Driver.pwm_list[idx].ChangeDutyCycle(0)

    # pygame로 소리 재생하는 코드!!
    @staticmethod
    def play_sound(sound, octave):
        # print ('play sound:%s' % sound)

        if octave:
            extra = '-2'
        else:
            extra = ''

        Driver.mysound = pygame.mixer.Sound('sound/%s%s.wav' % (sound, extra))
        Driver.mysound.play()

    @staticmethod
    def stop_sound():
        try:
            Driver.mysound.stop()
        except:
            return

    # lcd에 화면 출력하는 코드!
    # 16글자보다 안되면 16글자 맞춰서 스페이스 넣어서 이전 데이터가 안남아있게 한다!!
    @staticmethod
    def display(str, line):

        while len(str) < 16:
            str += ' '

        Driver.lcd.lcd_display_string(str, line)

    @staticmethod
    def display_ex(str, line):
        Driver.lcd.lcd_display_extended_string(str, line)
    
    @staticmethod
    def get_gunban_type():
        return Driver.gunban_type
    
    # 이거 잘 안됨. 그냥 안 하기로 합시다..ㅠㅠㅠ 이거 하고 싶었는데 내가 이걸 해낼 자신이 없다
    # 해낼 시간도 없다ㅠㅠ
    # @staticmethod
    # def lcd_cursor(is_on):
    #     if is_on:
    #         Driver.lcd.lcd_cursor_on()
    #     else:
    #         Driver.lcd.lcd_cursor_off()
    
    # @staticmethod
    # def lcd_gotoxy(x, y):
    #     Driver.lcd.lcd_gotoxy(x, y)
    
    @staticmethod
    def cleanup():
        for pwm in Driver.pwm_list:
            pwm.stop()

        GPIO.cleanup()

        Driver.lcd.lcd_clear()
