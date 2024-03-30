import pygame, os, sys, random, socket
from pygame.locals import *

#pygame init
pygame.init()
fpsClock = pygame.time.Clock()

#screen setup
width,height = 1000,700
mainSurface = pygame.display.set_mode((width,height))
pygame.display.set_caption('PONG CLIENT');
black = pygame.Color(0, 0, 0)

#text setup
letra50 = pygame.font.SysFont("Arial", 50)
letra30 = pygame.font.SysFont("Arial", 30)
texto_victoria = letra30.render(f"HAS GANADO", True, (255,255,255))
texto_derrota = letra30.render(f"HAS PERDIDO", True, (255,255,255))

# bat setup
bat1 = pygame.image.load('pong_bat.png')
bat2 = pygame.image.load('pong_bat.png')
batRect1 = bat1.get_rect()
batRect2 = bat2.get_rect()
player1Y = height/2
player2Y = height/2
player1X = 50
player2X = width-50
batRect1.center = (player1X, player1Y)
batRect2.center = (player2X, player2Y)

# ball setup
ball = pygame.image.load('ball.png')
ballRect = ball.get_rect()
bx = 0
by = 0
ballRect.center = (bx, by)
ballserved = False

#obstacles setup
obstacle = pygame.image.load('obstacle.png')
obstacles = []

#score setup
player_score = 0
client_score = 0
player_sets = 0
client_sets = 0
winner = "NONE"

#socket init
my_socket = socket.socket()
my_socket.connect(('localhost', 8000))

print("Connexion has been succesful!")
while True:
    
    data_str = my_socket.recv(1024).decode()
    data = eval(data_str)
    
    obstacles = []
    for obs_rect in data["obstacles"]:
        r_x, r_y, r_width, r_height = map(int, obs_rect.split(','))
        rect = pygame.Rect(r_x, r_y, r_width, r_height)
        obstacles.append(rect)
    
    bx = data["ball"][0]
    by = data["ball"][1]
    player1X = data["paddle1"][0]
    player1Y = data["paddle1"][1]
    player2X = data["paddle2"][0]
    player2Y = data["paddle2"][1]
    player_score = data["score"][0]
    player_sets = data["score"][1]
    client_score = data["score"][2]
    client_sets = data["score"][3]
    winner = data["winner"]
    mainSurface.fill(black)
    
    # events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    if keys[K_w]:
        my_socket.send("UP".encode())
    elif keys[K_s]:
        my_socket.send("DOWN".encode())
    else:
        my_socket.send("NONE".encode())
    
    ballRect.center = (bx, by)
    batRect1.center = (player1X, player1Y)
    batRect2.center = (player2X, player2Y)
        
    score_text = letra50.render(f"{client_score}       {player_score}", True, (200,200,200))
    sets_text = letra30.render(f"{client_sets}              {player_sets}", True, (200,200,200))
        
    for obs in obstacles:
        mainSurface.blit(obstacle, obs)
    mainSurface.blit(score_text, (425,50))
    mainSurface.blit(sets_text, (429,100))
    mainSurface.blit(ball, ballRect)
    mainSurface.blit(bat1, batRect1)
    mainSurface.blit(bat2, batRect2)
    pygame.draw.line(mainSurface,(255,255,255), (width/2, 0), (width/2, height))

    if winner != "NONE":
        mainSurface.fill((0,0,0))
        if winner == "HOST":
            mainSurface.blit(texto_derrota,(width/2-100,height/2-50))
        else:
            mainSurface.blit(texto_victoria,(width/2-100,height/2-50))
        pygame.display.update()
        pygame.time.wait(3000)
        winner = "NONE"
    
    fpsClock.tick(60)
    pygame.display.update()