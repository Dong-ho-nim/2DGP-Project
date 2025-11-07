from pico2d import *

class BackGround:
    def __init__(self):
        self.image = load_image('BackGround.png')

    def update(self):
        pass

    def draw(self):
        # 캔버스가 1280x720이므로 중앙은 (640, 360)
        print('BackGround.draw')
        self.image.draw(640, 360)

# class Sky:
#     def __init__(self):
#         self.image = load_image('Sky.png')
#
#     def update(self):
#         pass
#
#     def draw(self):
#         print('Sky.draw')
#         self.image.draw(640, 360)
#