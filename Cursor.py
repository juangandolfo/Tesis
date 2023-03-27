import pygame   
import random   
import numpy
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

    def update(self, speed):
        self.rect.move_ip(speed[0],speed[1])
        """if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)"""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

def getSpeedFromKeyboard(pressed_keys):
    if pressed_keys[K_UP]:
        speed=(0, -20)
    elif pressed_keys[K_DOWN]:
        speed=(0, 20)
    elif pressed_keys[K_LEFT]:
        speed=(-20, 0)
    elif pressed_keys[K_RIGHT]:
        speed=(20, 0)
    else:
        speed=(0,0)    
    return speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        """self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
        center=(random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),random.randint(0, SCREEN_HEIGHT),))
        self.speed = random.randint(5, 20)"""
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 0,0))
        self.rect = self.surf.get_rect(
        center=(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        self.speed = 0

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
    
    def moveEnemy(self,position):
        self.rect = self.surf.get_rect(
        center=position)

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
"""
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)
"""

clock = pygame.time.Clock()

player = Player()

enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

position=[(180,180),
           (100,SCREEN_HEIGHT/2),
           (180,SCREEN_HEIGHT-180),
           (SCREEN_WIDTH/2,100),
           (SCREEN_WIDTH-180,180),
           (SCREEN_WIDTH/2,SCREEN_HEIGHT-100),
           (SCREEN_WIDTH-100,SCREEN_HEIGHT/2),
           (SCREEN_WIDTH-180,SCREEN_HEIGHT-180),
           ]

for i in range(8):
    new_enemy = Enemy()
    new_enemy.moveEnemy(position[i])
    enemies.add(new_enemy)
    all_sprites.add(new_enemy)
    
pygame.key.set_repeat(50,0)

running = True

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running=False
        elif event.type == QUIT:
                running=False
        """elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)"""
        #surf = pygame.Surface((50, 50))
        #surf.fill((0, 0, 0))
        #rect = surf.get_rect()
        #surf_center = ((SCREEN_WIDTH-surf.get_width())/2,(SCREEN_HEIGHT-surf.get_height())/2)
        #screen.blit(surf, surf_center)
    
        screen.fill((0, 0, 0))
        pressed_keys = pygame.key.get_pressed()
        speed=getSpeedFromKeyboard(pressed_keys)
        player.update(speed)
        enemies.update()
        screen.blit(player.surf, player.rect)
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False
        pygame.display.flip()
        #clock.tick(60)


        
    

