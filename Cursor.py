#https://www.niit.com/india/knowledge-centre/python-game-development
#import Visualization_Client as VC
import socket
import time
import json
from collections import deque
from threading import Thread, Semaphore

import pygame   
import random   
import numpy
from tkinter import messagebox
from pygame.locals import (K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT,
                           K_ESCAPE,
                           KEYDOWN,
                           QUIT
                           )

import Processing_Module as PM
# Run Processing_Module

#Processing_Module_Client_thread = Thread(target=PM.Processing_Module_Client)
#Processing_Module_Server_thread = Thread(target=PM.Processing_Module_Server)
#Processing_Module_Client_thread.start()
#Processing_Module_Server_thread.start()



# TCP/IP visualization client ------------------------------------------------------------------------------

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT2 = 6002  # The port used by the API server

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT2))

#-----------------------------------------------------------------------------------------------------------

# Function to send the request and receive the data from MP
def Get_data():
        request = "GET /data"
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
        self.rect.move_ip((SCREEN_WIDTH-self.surf.get_width())/2,(SCREEN_HEIGHT-self.surf.get_width())/2)

    def update(self, speed):
        self.rect.move_ip(speed[0],-speed[1])
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

def getSpeedFromEMG():
    time.sleep(0.0005)
    data = Get_data()
    #print(f"Received {data!r}") 
    print([5*data[1],5*data[2]]) 
    speed=(20000*data[1]-20000*data[2],0)       
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
        self.name='Enemy'

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
objectives = pygame.sprite.Group()
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
        #surf_center = ((SCREEN_WIDTH-surf.get_width())/2,(SCREEN_HEIGHT-surf.get_height())/2)
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
            player.update((SCREEN_WIDTH/2-player.rect.center[0],SCREEN_HEIGHT/2-player.rect.center[1]))
            enemies.empty()
            GenerateEnemies()

        if pygame.sprite.spritecollideany(player, enemies):
            print('perdiste')
            player.update((SCREEN_WIDTH/2-player.rect.center[0],SCREEN_HEIGHT/2-player.rect.center[1]))
            
            #player.kill()
            #running = False
        pygame.display.flip()
        #clock.tick(60)


    


