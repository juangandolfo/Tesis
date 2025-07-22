#https://www.niit.com/india/knowledge-centre/python-game-development
#import Visualization_Client as VC
import socket
import json
import pygame
import random
from multiprocessing import Process
import msgpack as pack
import csv
import time
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
attemptTimeout = 3000 # milliseconds

position =  [(SCREEN_WIDTH/2,100),                 #norte
            (SCREEN_WIDTH-180,180),                 #noroeste
            (SCREEN_WIDTH-100,SCREEN_HEIGHT/2),     #este
            (SCREEN_WIDTH-180,SCREEN_HEIGHT-180),   #sureste
            (SCREEN_WIDTH/2,SCREEN_HEIGHT-100),     #sur
            (180,SCREEN_HEIGHT-180),                #suroeste
            (100,SCREEN_HEIGHT/2),                  #oeste
            (180,180),                              #noreste
            ]

objectiveList = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]


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
            print("[DEBUG] Attempting to connect to server...")
            client_socket.connect((HOST, PORT2))
            notConnected = False
            print("[DEBUG] Connected to server.")
        except Exception as e:
            print(f"[DEBUG] Connection failed: {e}")
            pass

#-----------------------------------------------------------------------------------------------------------
def Send_data(request):
    print(f"[DEBUG] Sending request: {request}")
    client_socket.settimeout(100)
    try:
        client_socket.sendall(request.encode())
        try:
            data = client_socket.recv(1024)
            print(f"[DEBUG] Received raw data: {data}")
            response_data = pack.unpackb(data, raw=False)
            print(f"[DEBUG] Unpacked response data: {response_data}")
        except socket.timeout as e:
            print(f"[DEBUG] Socket timeout: {e}")
        except socket.error as e:
            print(f"[DEBUG] Socket error: {e}")
    except (socket.timeout, socket.error) as e:
        print(f"[DEBUG] Communication error: {e}")
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Get_data():
    print("[DEBUG] Calling Get_data()")
    request = "GET /data1"
    response_data = Send_data(request)
    print(f"[DEBUG] Get_data() response: {response_data}")
    return response_data

#-----------------------------------------------------------------------------------------------------------
def Post_start():
    print(f"[DEBUG] Calling Post_start() with objectiveEnemy={objectiveEnemy}")
    request = "POST /startAttempt " + str(objectiveEnemy)
    try:
        response_data = Send_data(request)
        print(f"[DEBUG] Post_start() response: {response_data}")
        if response_data == "Ok":
            startAttemptTimer()
            return 
        else:
            messagebox.alert(text='Error in starting the attempt', title='Error', button='OK')
    except Exception as e:
        print(f"[DEBUG] Exception in Post_start: {e}")
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
    global position, enemies, objectives, all_sprites, objectiveEnemy
    print("[DEBUG] Generating enemies from list")
    attempt = Get_attempt()
    print(f"[DEBUG] Current attempt: {attempt}")
    objectiveEnemy = objectiveList[attempt % len(objectiveList)]
    print(f"[DEBUG] Selected objectiveEnemy: {objectiveEnemy}")
    GenerateEnemies(objectiveEnemy)

# ----------------------------------------------------------------------------------------------------------
def GenerateEnemies(objective):
    global position,enemies, objectives, all_sprites
    print(f"[DEBUG] Generating enemies, objective index: {objective}")
    KillEnemies()
    objective = objective - 1
    for i in range(8):
        if i == objective:
            print(f"[DEBUG] Placing objective at position {i}: {position[i]}")
            objective= Enemy()
            objective.name='objective'
            objective.surf.fill((0,255,0))
            objective.moveEnemy(position[i])
            objectives.add(objective)
            all_sprites.add(objective)
        else:
            print(f"[DEBUG] Placing enemy at position {i}: {position[i]}")
            new_enemy = Enemy()
            new_enemy.surf.fill((255,0,0))
            new_enemy.moveEnemy(position[i])
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

# ----------------------------------------------------------------------------------------------------------
def KillEnemies():
    print("[DEBUG] Killing all enemies and objectives")
    for objective in objectives:
        objective.kill()
    enemies.empty()

# ----------------------------------------------------------------------------------------------------------
def returnToCenter():
    global player
    print("[DEBUG] Returning player to center")
    player.update((SCREEN_WIDTH/2-player.rect.center[0],-SCREEN_HEIGHT/2+player.rect.center[1]))

# ----------------------------------------------------------------------------------------------------------
def restartAttempt():
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global player, enemies, objectives, all_sprites
    print("[DEBUG] Restarting attempt")
    returnToCenter()
    KillEnemies()
    GenerateEnemiesFromList()

# ----------------------------------------------------------------------------------------------------------
def getSpeedFromKeyboard(pressed_keys):
    # This function returns the speed of the cursor based on the keys pressed
    print(f"[DEBUG] Getting speed from keyboard: {pressed_keys}")
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
    print(f"[DEBUG] Keyboard speed: {speed}")
    return speed

# ----------------------------------------------------------------------------------------------------------
def getSpeedFromEMG():
    # This function returns the speed of the cursor based on the EMG data
    speed = [0,0]
    try:
        speed = Get_data()
        print(f"[DEBUG] EMG speed: {speed}")
    except Exception as e:
        print(f"[DEBUG] Exception in getSpeedFromEMG: {e}")
    return speed

# ----------------------------------------------------------------------------------------------------------
def addText():
    global text1, text2,screen
    print("[DEBUG] Adding text to screen")
    text1 = font.render("Press Enter to start or restart", True, (255, 255, 255))
    text2 = font.render("Press Esc to exit", True, (255, 255, 255))
    screen.blit(text1, (250, 380))
    screen.blit(text2, (250, 400))
    
# ----------------------------------------------------------------------------------------------------------
def EraseText():
    global text1, text2
    print("[DEBUG] Erasing text from screen")
    text1 = font.render("", True, (255, 255, 255))
    text2 = font.render("", True, (255, 255, 255))

# ----------------------------------------------------------------------------------------------------------
def startAttemptTimer():
    global attemptTimer
    print("[DEBUG] Starting attempt timer")
    attemptTimer = time.time()  # Start the timer

# ----------------------------------------------------------------------------------------------------------
def checkAttemptTiemout():
    global attemptTimer, attemptTimeout
    elapsed = (time.time() - attemptTimer)*1000
    print(f"[DEBUG] Checking attempt timeout: elapsed={elapsed} ms, timeout={attemptTimeout} ms")
    if elapsed > attemptTimeout:  # Check if the timeout has been reached
        print("[DEBUG] Attempt timed out")
        Post_Loss()
        returnToCenter()
        KillEnemies()
        GenerateEnemiesFromList()
        Post_start()


### CALLBACKS ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
def K_Return_Callback():
    global started
    print(f"[DEBUG] K_RETURN pressed. started={started}")
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
    print("[DEBUG] K_ESCAPE pressed. Exiting.")
    Post_Exit()
    running = False

# ----------------------------------------------------------------------------------------------------------
def k_1_Callback():
    print("[DEBUG] k_1 pressed")
    GenerateEnemies(1)

def k_2_Callback():
    print("[DEBUG] k_2 pressed")
    GenerateEnemies(2)

def k_3_Callback():
    print("[DEBUG] k_3 pressed")
    GenerateEnemies(3)

def k_4_Callback():
    print("[DEBUG] k_4 pressed")
    GenerateEnemies(4)

def k_5_Callback():
    print("[DEBUG] k_5 pressed")
    GenerateEnemies(5)

def k_6_Callback():
    print("[DEBUG] k_6 pressed")
    GenerateEnemies(6)

def k_7_Callback():
    print("[DEBUG] k_7 pressed")
    GenerateEnemies(7)

def k_8_Callback():
    print("[DEBUG] k_8 pressed")
    GenerateEnemies(8)

### EVENTS -------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
def HandleEvents():
    global running, started
    for event in pygame.event.get():
        print(f"[DEBUG] Event: {event}")
        if event.type == QUIT:
            print("[DEBUG] QUIT event received")
            running = False
        elif event.type == pygame.KEYUP:
            print(f"[DEBUG] KEYUP event: {event.key}")
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
        print("[DEBUG] Player collided with objective")
        HandleCollideObjective()

def HandleCollideObjective():
    global started
    print("[DEBUG] Handling collision with objective")
    Post_Win()
    returnToCenter()
    KillEnemies()
    GenerateEnemiesFromList()
    Post_start()
    # started = False

def CheckCollideEnemy():
    if pygame.sprite.spritecollideany(player, enemies):
        print("[DEBUG] Player collided with enemy")
        HandleCollideEnemy()

def HandleCollideEnemy():
    global started 
    print("[DEBUG] Handling collision with enemy")
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
    
    print("[DEBUG] Starting Cursor()")
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
        print("[DEBUG] Main loop iteration")
        HandleEvents()
        
        screen.fill((0, 0, 0))        
        speed=getSpeedFromEMG()
        print(f"[DEBUG] Player speed: {speed}")
        if started:
            EraseText()
            player.update(speed)
            checkAttemptTiemout()
        else:
            addText()

        screen.blit(player.surf, player.rect)
        
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        CheckCollideObjective()
        CheckCollideEnemy()

        pygame.display.flip()
        
if __name__ == '__main__':
    print("[DEBUG] __main__ starting Cursor process")
    Cursor_Process = Process(target=Cursor)
    Cursor_Process.start()
