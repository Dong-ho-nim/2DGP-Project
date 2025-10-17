from pico2d import *

class Fighter:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 50, 100)  # 캐릭터 크기
        self.color = color
        self.hp = 100
        self.speed = 5
        self.attack_power = 10
        self.is_attacking = False


