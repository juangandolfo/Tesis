import pygame   
import random   
from pygame.locals import (K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT,
                           K_ESCAPE,
                           KEYDOWN,
                           QUIT
                           )

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.rect.move_ip((SCREEN_WIDTH-self.surf.get_width())/2,(SCREEN_HEIGHT-self.surf.get_width())/2)

def update(self, pressed_keys):
    if pressed_keys[K_UP]:
        self.rect.move_ip(0, -5)
    if pressed_keys[K_DOWN]:
        self.rect.move_ip(0, 5)
    if pressed_keys[K_LEFT]:
        self.rect.move_ip(-5, 0)
    if pressed_keys[K_RIGHT]:
        self.rect.move_ip(5, 0)
    if self.rect.left < 0:
        self.rect.left = 0
    if self.rect.right > SCREEN_WIDTH:
        self.rect.right = SCREEN_WIDTH
    if self.rect.top <= 0:
        self.rect.top = 0
    if self.rect.bottom >= SCREEN_HEIGHT:
        self.rect.bottom = SCREEN_HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
        center=(random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),random.randint(0, SCREEN_HEIGHT),))
        self.speed = random.randint(5, 20)
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player = Player()
player.__init__()

running = True

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running=False
        elif event.type == QUIT:
                running=False
        screen.fill((255, 255, 255))
        #surf = pygame.Surface((50, 50))
        #surf.fill((0, 0, 0))
        #rect = surf.get_rect()
        #surf_center = ((SCREEN_WIDTH-surf.get_width())/2,(SCREEN_HEIGHT-surf.get_height())/2)
        #screen.blit(surf, surf_center)
        
        screen.fill((0, 0, 0))
        pressed_keys = pygame.key.get_pressed()
        update(player,pressed_keys)
        screen.blit(player.surf, player.rect)
        pygame.display.flip()
    

