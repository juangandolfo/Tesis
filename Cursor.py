#https://www.niit.com/india/knowledge-centre/python-game-development
#import Visualization_Client as VC
import socket
import json
import pygame
import random
from multiprocessing import Process
#from tkinter import messagebox
import pymsgbox as messagebox
from pygame.locals import (K_UP,
                           K_DOWN,
                           K_LEFT,
                           K_RIGHT,
                           K_ESCAPE,
                           KEYDOWN,
                           QUIT
                           )

# PARAMETERS -----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
frequency = 120
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

position=[(180,180),
        (100,SCREEN_HEIGHT/2),
        (180,SCREEN_HEIGHT-180),
        (SCREEN_WIDTH/2,100),
        (SCREEN_WIDTH-180,180),
        (SCREEN_WIDTH/2,SCREEN_HEIGHT-100),
        (SCREEN_WIDTH-100,SCREEN_HEIGHT/2),
        (SCREEN_WIDTH-180,SCREEN_HEIGHT-180),
        ]

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT2 = 6002  # The port used by the MP Server


# TCP/IP Cursor client -------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket

#-----------------------------------------------------------------------------------------------------------
def Connect():
    notConnected = True
    while notConnected:
        try:
            client_socket.connect((HOST, PORT2))
            notConnected = False
        except Exception as e:
            #print(e)
            pass
    
#-----------------------------------------------------------------------------------------------------------
def Get_data():
    # Function to send the request and receive data from MP
    request = "GET /data1"
    client_socket.settimeout(3)
    try:
        client_socket.sendall(request.encode())
        try:
            data = client_socket.recv(1024)
            response_data = json.loads(data.decode()) # Decode the received data
        except socket.timeout as e:
            print(e)
        except socket.error as e:
            print(e)
    except (socket.timeout, socket.error) as e:
        print(f"Communication error: {e}")
    return response_data

# CLASSES --------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill((255, 255, 255))
        #self.surf=pygame.draw.circle(self.surf, (255,255,255), (400,400),5)
        self.rect = self.surf.get_rect()
        self.rect.move_ip((SCREEN_WIDTH-self.surf.get_width())/2,(SCREEN_HEIGHT-self.surf.get_width())/2)

    def update(self, speed):
        try:
            self.rect.move_ip(speed[0],-speed[1])
        except:
            self.rect.move_ip(0,0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

#-----------------------------------------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 0,0))
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        self.speed = 0
        self.name='Enemy'

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

    def moveEnemy(self,position):
        self.rect = self.surf.get_rect(center=position)

# INSTANCES ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
player = Player()
enemies = pygame.sprite.Group()
objectives = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# FUNCTIONS ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def GenerateEnemies():
    global position, enemies, objectives, all_sprites

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

# ----------------------------------------------------------------------------------------------------------
def getSpeedFromKeyboard(pressed_keys):
    # This function returns the speed of the cursor based on the keys pressed
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

# ----------------------------------------------------------------------------------------------------------
def getSpeedFromEMG():
    # This function returns the speed of the cursor based on the EMG data
    speed = [0,0]
    try:
        speed = Get_data()
    except Exception as e:
        print(e)
    return speed

# MAIN LOOP ------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def Cursor():
    # set up the display and communication
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global player, enemies, objectives, all_sprites
    
    Connect() 
    pygame.init()
    pygame.key.set_repeat(50,0)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    GenerateEnemies()
    
    running = True
    while running:
        # Main loop
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False 

        screen.fill((0, 0, 0))        

        speed=getSpeedFromEMG()
        player.update(speed)
        screen.blit(player.surf, player.rect)
        
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        if pygame.sprite.spritecollideany(player, objectives):
            #messagebox.showinfo('Y el TITULO?!?!','YA ANDA! (ponenos S plz)') #este es con TKinter
            #messagebox.alert(text='Ganaste', title='Y el TITULO?!?!', button='OK') #este es con pymsgbox
            print('ganaste')
            player.update((SCREEN_WIDTH/2-player.rect.center[1],SCREEN_HEIGHT/2-player.rect.center[0]))
            for objective in objectives:
                objective.kill()
            enemies.empty()
            GenerateEnemies()

        if pygame.sprite.spritecollideany(player, enemies):
            print('perdiste')
            player.update((SCREEN_WIDTH/2-player.rect.center[0],SCREEN_HEIGHT/2-player.rect.center[1]))

        pygame.display.flip()
        
if __name__ == '__main__':
    Cursor_Process = Process(target=Cursor)
    Cursor_Process.start()
