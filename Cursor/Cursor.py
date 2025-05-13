#https://www.niit.com/india/knowledge-centre/python-game-development
#import Visualization_Client as VC
import socket
import json
import pygame
import random
from multiprocessing import Process
import msgpack as pack
import csv
import pymsgbox as messagebox
from pygame.locals import   (K_UP,
                            K_DOWN,
                            K_LEFT,
                            K_RIGHT,
                            K_ESCAPE,
                            KEYDOWN,
                            K_KP_ENTER,
                            K_SPACE,
                            K_RETURN,
                            K_1,
                            K_2,
                            K_3,
                            K_4,
                            K_5,
                            K_6,
                            K_7,
                            K_8,
                            QUIT
                            )

### PARAMETERS ---------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
frequency = 120
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

position =  [(SCREEN_WIDTH/2,100),                 #norte
            (SCREEN_WIDTH-180,180),                 #noroeste
            (SCREEN_WIDTH-100,SCREEN_HEIGHT/2),     #este
            (SCREEN_WIDTH-180,SCREEN_HEIGHT-180),   #sureste
            (SCREEN_WIDTH/2,SCREEN_HEIGHT-100),     #sur
            (180,SCREEN_HEIGHT-180),                #suroeste
            (100,SCREEN_HEIGHT/2),                  #oeste
            (180,180),                              #noreste
            ]

objectiveList = [1,2,3,4,5,6,7,8,8,7,6,5,4,3,2,1]


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
def Send_data(request):
    # Function to send the request and receive data from MP
    client_socket.settimeout(100)
    try:
        client_socket.sendall(request.encode())
        try:
            data = client_socket.recv(1024)
            response_data = pack.unpackb(data, raw=False)
        except socket.timeout as e:
            print(e)
        except socket.error as e:
            print(e)
    except (socket.timeout, socket.error) as e:
        print(f"Communication error: {e}")
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Get_data():
    # Function to send the request and receive data from MP
    request = "GET /data1"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_start():
    # Function to send the request and receive data from MP
    request = "POST /startAttempt"
    try:
        response_data = Send_data(request)
        if response_data == "Ok":
            return 
        else:
            messagebox.alert(text='Error in starting the attempt', title='Error', button='OK')
    except Exception as e:
        messagebox.alert(text='Error in starting the attempt sending', title='Error', button='OK')

#-----------------------------------------------------------------------------------------------------------
def Post_Win():
    # Function to send the request and receive data from MP
    request = "POST /win"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_Loss():
    # Function to send the request and receive data from MP
    request = "POST /loss"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_Restart():
    # Function to send the request and receive data from MP
    request = "POST /restartAttempt"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_Exit():
    # Function to send the request and receive data from MP
    request = "POST /exit"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Get_attempt():
    # Function to send the request and receive data from MP
    request = "GET /attempt"
    response_data = Send_data(request)
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_cursorStart():
    # Function to send the request and receive data from MP
    request = "POST /cursorStart"
    response_data = Send_data(request)
    return response_data

### CLASSES ------------------------------------------------------------------------------------------------
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

### INSTANCES ----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
player = Player()
enemies = pygame.sprite.Group()
objectives = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)


### FUNCTIONS ----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def GenerateEnemiesFromList():
    global position, enemies, objectives, all_sprites
    # objectiveEnemy=random.randint(1,8)
    attempt = Get_attempt()
    objectiveEnemy = objectiveList[attempt % len(objectiveList)]
    GenerateEnemies(objectiveEnemy)

# ----------------------------------------------------------------------------------------------------------
def GenerateEnemies(objective):
    global position,enemies, objectives, all_sprites
    KillEnemies()
    objective = objective - 1
    for i in range(8):
        if i == objective:
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
def KillEnemies():
    for objective in objectives:
        objective.kill()
    enemies.empty()

# ----------------------------------------------------------------------------------------------------------
def returnToCenter():
    global player
    player.update((SCREEN_WIDTH/2-player.rect.center[0],-SCREEN_HEIGHT/2+player.rect.center[1]))

# ----------------------------------------------------------------------------------------------------------
def restartAttempt():
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global player, enemies, objectives, all_sprites
    
    returnToCenter()
    KillEnemies()
    GenerateEnemiesFromList()

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
        print(f"--------------------------------------------{speed}")
    except Exception as e:
        print(e)
    return speed

# ----------------------------------------------------------------------------------------------------------
def addText():
    global text1, text2,screen
    text1 = font.render("Press Enter to start or restart", True, (255, 255, 255))
    text2 = font.render("Press Esc to exit", True, (255, 255, 255))
    screen.blit(text1, (250, 380))
    screen.blit(text2, (250, 400))
    
# ----------------------------------------------------------------------------------------------------------
def EraseText():
    global text1, text2
    text1 = font.render("", True, (255, 255, 255))
    text2 = font.render("", True, (255, 255, 255))

### CALLBACKS ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
def K_Return_Callback():
    global started
    if started:
        Post_Restart()
        restartAttempt()
        started = False
    else:
        Post_start()
        getSpeedFromEMG()
        started = True

# ----------------------------------------------------------------------------------------------------------
def K_Escape_Callback():
    global running
    #messagebox.alert(text='Exit', title='Exit', button='OK')
    Post_Exit()
    running = False

# ----------------------------------------------------------------------------------------------------------
def k_1_Callback():
    GenerateEnemies(1)

# ----------------------------------------------------------------------------------------------------------
def k_2_Callback():
    GenerateEnemies(2)

# ----------------------------------------------------------------------------------------------------------
def k_3_Callback():
    GenerateEnemies(3)

# ----------------------------------------------------------------------------------------------------------
def k_4_Callback():
    GenerateEnemies(4)

# ----------------------------------------------------------------------------------------------------------
def k_5_Callback():
    GenerateEnemies(5)

# ----------------------------------------------------------------------------------------------------------
def k_6_Callback():
    GenerateEnemies(6)

# ----------------------------------------------------------------------------------------------------------
def k_7_Callback():
    GenerateEnemies(7)

# ----------------------------------------------------------------------------------------------------------
def k_8_Callback():
    GenerateEnemies(8)

### EVENTS -------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
def HandleEvents():
    global running, started
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == K_ESCAPE:
                K_Escape_Callback()
            if event.key == K_RETURN:
                K_Return_Callback()
            if not started:
                if event.key == K_1:
                    k_1_Callback()
                if event.key == K_2:
                    k_2_Callback()
                if event.key == K_3:
                    k_3_Callback()
                if event.key == K_4:
                    k_4_Callback()
                if event.key == K_5:
                    k_5_Callback()
                if event.key == K_6:
                    k_6_Callback()
                if event.key == K_7:
                    k_7_Callback()
                if event.key == K_8:
                    k_8_Callback()

# ----------------------------------------------------------------------------------------------------------
def CheckCollideObjective():
    if pygame.sprite.spritecollideany(player, objectives):
        HandleCollideObjective()

# ----------------------------------------------------------------------------------------------------------
def HandleCollideObjective():
    global started
    Post_Win()
    returnToCenter()
    KillEnemies()
    GenerateEnemiesFromList()
    Post_start()
    # started = False
        
# ----------------------------------------------------------------------------------------------------------
def CheckCollideEnemy():
    if pygame.sprite.spritecollideany(player, enemies):
        HandleCollideEnemy()

# ----------------------------------------------------------------------------------------------------------
def HandleCollideEnemy():
    global started 
    Post_Loss()
    returnToCenter()
    KillEnemies()
    GenerateEnemiesFromList()
    Post_start()
    # started = False   

### MAIN LOOP ----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------
def Cursor():
    # set up the display and communication
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global player, enemies, objectives, all_sprites,running, font, started, screen, text1, text2
    
    Connect()
    Post_cursorStart() 
    pygame.init()
    pygame.key.set_repeat(50,0)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, 36)
    
    GenerateEnemiesFromList()
    
    running = True
    started = False
    while running:
        # Main loop
        HandleEvents()
        
        screen.fill((0, 0, 0))        
        speed=getSpeedFromEMG()
        if started:
            EraseText()
            player.update(speed)
        else:
            addText()

        screen.blit(player.surf, player.rect)
        
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        CheckCollideObjective()
        CheckCollideEnemy()

        pygame.display.flip()
        
if __name__ == '__main__':
    Cursor_Process = Process(target=Cursor)
    Cursor_Process.start()
