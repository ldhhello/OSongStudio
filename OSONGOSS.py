import os

# 파일 입출력을 처리하는 클래스
# 음악이 song_data에 저장되고, open_file, write_file로 음악을 파일로 쓰거나 파일에서 읽어올 수 있다
class OsongOSS:
    song_data = []
    song_len = -1
    current_idx = 0

    # .osongoss 파일을 여는 함수
    def open_file(self, filename):
        # print ('filename %s' % filename)

        self.initialize()

        f = open(filename, 'r')
        lines = f.readlines()

        for line in lines:

            line = line.strip()

            if line == '':
                continue

            if line[0] == '#':
                continue

            data = line.split(' ')
            if len(data) < 2 or len(data) >= 4:
                # print ('File format is invalid')
                break

            score = data[0]
            length = float(data[1])
            octave = False
            if len(data) == 3 and data[2] == '1':
                octave = True

            self.song_data.append([score, length, octave])

        f.close()

        length = 0

        for s in self.song_data:
            length += s[1]

        self.song_len = length

    def initialize(self):
        self.song_data = []
        self.song_len = 0
        self.current_idx = 0

    # 현재 악보의 전체 길이 (초 단위) 를 반환하는 함수
    def song_length(self):
        # print ('song_length: %.2f' % self.song_len)
        return self.song_len

    # 악보에서 지금까지 읽은 부분 다음 음을 반환하는 함수
    def next_(self):
        if self.current_idx >= len(self.song_data):
            return {"score":-3000}

        ret_val = {"score":self.song_data[self.current_idx][0],
            "length":self.song_data[self.current_idx][1],
            "octave":self.song_data[self.current_idx][2]}

        self.current_idx += 1

        return ret_val

    # 현재 악보에 음 추가하는 함수
    def append(self, score, length, octave):
        self.song_data.append([score, length, octave])

    # OsongOSS 파일 쓰는(Write) 함수
    def write_file(self, filename):

        if os.path.exists(filename):
            return False

        if len(self.song_data) == 0:
            return True

        f = open(filename, 'w')

        f.write('# OSONGOSS File, Created by OSongStudio\n')

        for s in self.song_data:
            f.write('%s %f %d\n' % (s[0], s[1], s[2]))

        f.close()

        return True