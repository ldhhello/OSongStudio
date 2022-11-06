# 라즈베리 파이 환경이 아닌, 일반적인 PC 환경에서 LCD 라이브러리를 사용할 수 있게 해주는 코드!
# 진짜 LCD처럼 돌아가지는 않지만 그래도 디버깅은 가능할 정도로는 나온다!!

class drivers:
    @staticmethod
    def Lcd():
        return LCDOsong()

    @staticmethod
    def CustomCharacters(lcdosong):
        return CustomOsong()
        


class LCDOsong:
    def lcd_display_string(self, str, line):
        print ('LCD line %d: %s' % (line, str))
    
    def lcd_display_extended_string(self, str, line):
        print ('LCD line %d: %s (Ex)' % (line, str))

    def lcd_clear(self):
        print ('Clear osong~~')

    def lcd_cursor_on(self):
        print ('LCD Cursor is on')

    def lcd_cursor_off(self):
        print ('LCD Cursor is off')

    def lcd_gotoxy(self, x, y):
        print ('Cursor position: (%d, %d)' % (x, y))
        
class CustomOsong:
    char_1_data = []
    char_2_data = []
    char_3_data = []
    char_4_data = []
    char_5_data = []
    char_6_data = []
    char_7_data = []
    char_8_data = []

    def load_custom_characters_data(self):
        print ('Custom Characters loaded!')