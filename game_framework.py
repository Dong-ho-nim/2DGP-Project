from pico2d import *

class Fighter:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 50, 100)  # 캐릭터 크기
        self.color = color
        self.hp = 100
        self.speed = 5
        self.attack_power = 10
        self.is_attacking = False

    def handle_input(self, keys, left=True):
        if left:
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_d]:
                self.rect.x += self.speed
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_s]:
                self.rect.y += self.speed
            if keys[pygame.K_SPACE]:
                self.is_attacking = True
        else:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.rect.y += self.speed
            if keys[pygame.K_RETURN]:
                self.is_attacking = True

