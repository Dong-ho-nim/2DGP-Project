# BackGround.py
from pico2d import load_image

class BackGround:
    def __init__(self):
        self.image = load_image('background.png')   # 프로젝트 루트에 배경 넣기
    def update(self): pass
    def draw(self):
        self.image.draw(600, 350)   # 1200×700 캔버스 중앙