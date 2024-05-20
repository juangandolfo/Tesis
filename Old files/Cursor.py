#https://www.niit.com/india/knowledge-centre/python-game-development
#import Visualization_Client as VC
import socket
import time
import json
from collections import deque
from threading import Thread, Semaphore

import pygame   
import random   
from tkinter import messagebox
from pygame.locals import (K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT,
                           K_ESCAPE,
                           KEYDOWN,
                           QUIT
                           )

# TCP/IP Cursor client ------------------------------------------------------------------------------

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT2 = 6002  # The port used by the API server

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT2))

frequency = 1
#-----------------------------------------------------------------------------------------------------------

# Function to send the request and receive the data from MP
def Get_data():
        request = "GET /data1"
        client_socket.sendall(request.encode())
        data = client_socket.recv(1024)
        response_data = json.loads(data.decode()) # Decode the received data
        return response_data
# ----------------------------------------------------------------------------------------------------------

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        #self.surf=pygame.draw.circle(self.surf, (255,255,255), (400,400),5)
        self.rect = self.surf.get_rect()
        self.rect.move_ip((Cursor.SCREEN_WIDTH-self.surf.get_width())/2,(Cursor.SCREEN_HEIGHT-self.surf.get_width())/2)

    def update(self, speed):
        try:
            self.rect.move_ip(speed[0],speed[1])
        except:
            self.rect.move_ip(0,0)
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
        if self.rect.right > Cursor.SCREEN_WIDTH:
            self.rect.right = Cursor.SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= Cursor.SCREEN_HEIGHT:
            self.rect.bottom = Cursor.SCREEN_HEIGHT

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

def getSpeedFromEMG():
    time.sleep(1/frequency)
    data = Get_data()
    print("Client1:", data) 
    speed=(data[1],data[2])
    #print(speed)
    return speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        """self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
        center=(random.randint(Cursor.SCREEN_WIDTH + 20, Cursor.SCREEN_WIDTH + 100),random.randint(0, Cursor.SCREEN_HEIGHT),))
        self.speed = random.randint(5, 20)"""
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 0,0))
        self.rect = self.surf.get_rect(
        center=(Cursor.SCREEN_WIDTH - 100, Cursor.SCREEN_HEIGHT - 100))
        self.speed = 0
        self.name='Enemy'

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
    
    def moveEnemy(self,position):
        self.rect = self.surf.get_rect(
        center=position)

def Cursor():
    pygame.init()
    Cursor.SCREEN_WIDTH = 800
    Cursor.SCREEN_HEIGHT = 800

    screen = pygame.display.set_mode((Cursor.SCREEN_WIDTH, Cursor.SCREEN_HEIGHT))
    """
    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 250)
    """

    clock = pygame.time.Clock()

    player = Player()

    enemies = pygame.sprite.Group()
    objectives = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    position=[(180,180),
            (100,Cursor.SCREEN_HEIGHT/2),
            (180,Cursor.SCREEN_HEIGHT-180),
            (Cursor.SCREEN_WIDTH/2,100),
            (Cursor.SCREEN_WIDTH-180,180),
            (Cursor.SCREEN_WIDTH/2,Cursor.SCREEN_HEIGHT-100),
            (Cursor.SCREEN_WIDTH-100,Cursor.SCREEN_HEIGHT/2),
            (Cursor.SCREEN_WIDTH-180,Cursor.SCREEN_HEIGHT-180),
            ]
    def GenerateEnemies():
        objectiveEnemy=random.randint(0,7)
        for i in range(8): 
            if i == objectiveEnemy:
                objective= Enemy()
                objective.name='objective'
                objective.surf.fill((0,255,0))
                objective.moveEnemy(position[i])
                objectives.add(objective)
                all_sprites.add(objective)
            else:
                new_enemy = Enemy()
                new_enemy.surf.fill((255,0,0))
                new_enemy.moveEnemy(position[i])
                enemies.add(new_enemy)
                all_sprites.add(new_enemy) 
            """new_enemy = Enemy()
            if i == objectiveEnemy :
                new_enemy.surf.fill((0,255,0))
            new_enemy.moveEnemy(position[i])
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)"""
        
    pygame.key.set_repeat(50,0)

    running = True
    GenerateEnemies()

    while running:    
        #for event in pygame.event.get():
            #if event.type == KEYDOWN:
            # if event.key == K_ESCAPE:
                #  running=False
        # elif event.type == QUIT:
                # running=False
            """elif event.type == ADDENEMY:
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)"""
            #surf = pygame.Surface((50, 50))
            #surf.fill((0, 0, 0))
            #rect = surf.get_rect()
            #surf_center = ((Cursor.SCREEN_WIDTH-surf.get_width())/2,(Cursor.SCREEN_HEIGHT-surf.get_height())/2)
            #screen.blit(surf, surf_center)
        
            screen.fill((0, 0, 0))
            #pressed_keys = pygame.key.get_pressed()
            #speed=getSpeedFromKeyboard(pressed_keys)
            speed=getSpeedFromEMG()
            player.update(speed)
            enemies.update()
            screen.blit(player.surf, player.rect)
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            
            if pygame.sprite.spritecollideany(player, objectives):
                messagebox.showerror('You did it!!!!!!!!!!!!!!!','Lograste llegar al objetivo crackkk!!')
                player.update((Cursor.SCREEN_WIDTH/2-player.rect.center[0],Cursor.SCREEN_HEIGHT/2-player.rect.center[1]))
                enemies.empty()
                GenerateEnemies()

            if pygame.sprite.spritecollideany(player, enemies):
                print('perdiste')
                player.update((Cursor.SCREEN_WIDTH/2-player.rect.center[0],Cursor.SCREEN_HEIGHT/2-player.rect.center[1]))
                
                #player.kill()
                #running = False
            pygame.display.flip()
            #clock.tick(60)


    


