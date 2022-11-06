from Driver import Driver

# LCD상에서 프로그레스바 구현하는 코드
class ProgressBar:

    is_play = False
    
    value = 0
    max_val = 0
    title = ''

    # 이거 {0x02} {0x03} 이런거는 CustomCharacter.py에 있음!!
    progress_str = [
        ['{0x02}', '{0x03}'],
        ['{0x04}', '{0x05}'],
        ['{0x06}', '{0x07}']
    ]

    # 프로그레스바 켜는 코드
    def enable(self, is_play, val, max_val, title):
        self.is_play = is_play
        self.max_val = max_val
        self.value = val
        self.title = title

        while len(self.title) < 14:
            self.title += ' '

        Driver.change_character(Driver.CUSTOMCHARACTER_PROGRESSBAR)
        self.display()

    # 프로그레스바 끄는 코드
    def disable(self):
        Driver.display('', 1)
        Driver.display('', 2)

        Driver.change_character(Driver.CUSTOMCHARACTER_DEFAULT)

    # 프로그레스바 값 바꾸는 코드
    def change_value(self, val):
        self.value = val
        self.display()

    # 프로그레스바를 lcd에 출력하는 코드
    def display(self):

        if self.is_play:
            play_str = '{0x00}'
        else:
            play_str = '{0x01}'

        Driver.display_ex('%s %s' % (play_str, self.title), 1)
        
        progressbar_sz = 14
        percent = self.value / self.max_val

        progress_str = ''

        for i in range(progressbar_sz):
            if i == 0:
                bar_type = 0
            elif i == progressbar_sz - 1:
                bar_type = 2
            else:
                bar_type = 1

            if i < percent * progressbar_sz:
                now = 1
            else:
                now = 0

            progress_str += ProgressBar.progress_str[bar_type][now]

        Driver.display_ex(' %s ' % progress_str, 2)
            