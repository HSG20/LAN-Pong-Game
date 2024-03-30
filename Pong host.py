import pygame, os, sys, random, socket
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

my_socket = socket.socket()
my_socket.bind(("localhost", 8000))
my_socket.listen(5)

player_score = 0
client_score = 0
player_sets = 0
client_sets = 0
dificultad = 6.5

width,height = 1000,700
mainSurface = pygame.display.set_mode((width,height))
pygame.display.set_caption('PONG HOST');
black = pygame.Color(0, 0, 0)
letra50 = pygame.font.SysFont("Arial", 50)
letra30 = pygame.font.SysFont("Arial", 30)

texto_victoria = letra30.render(f"HAS GANADO", True, (255,255,255))
texto_derrota = letra30.render(f"HAS PERDIDO", True, (255,255,255))

# bat init
bat1 = pygame.image.load('pong_bat.png')
bat2 = pygame.image.load('pong_bat.png')
player1Y = height/2
player2Y = height/2
player1X = 50
player2X = width-50
batRect1 = bat1.get_rect()
batRect2 = bat2.get_rect()

# ball init
velocidad = 8
ball = pygame.image.load('ball.png')
ballRect = ball.get_rect()
bx, by = (width/2, 3*height/4)
sx, sy = (velocidad, velocidad)
ballRect.center = (bx, by)
ballserved = False

obstacle = pygame.image.load('obstacle.png')
obstacles = []
winner = "NONE"

def random_obstacle(player):
    obstacleY = random.randint(30,height-30)
    obstacleX = (random.randint(0, 190) + 180) + (player*430)
    obs_width = obstacle.get_width()
    obs_height = obstacle.get_height()
    obstacle_rect = Rect(obstacleX, obstacleY, obs_width, obs_height)
    obstacles.append(obstacle_rect)
    return obstacles

batRect1.center = (player1X, player1Y)
batRect2.center = (player2X, player2Y)

connexion, addr = my_socket.accept()
print("New connection established")
print(addr)

while True:
    
    obstacles_ready = []
    for obs_rect in obstacles:
        obstacles_ready.append(f"{obs_rect.x},{obs_rect.y},{obs_rect.width},{obs_rect.height}")
        
    data = {"ball": [bx,by], "obstacles": obstacles_ready, "paddle1": [player1X,player1Y],
        "paddle2": [player2X,player2Y], "score": [player_score, player_sets, client_score, client_sets],
        "winner": winner}
    connexion.send(str(data).encode())
    
    if winner != "NONE":
        pygame.time.wait(3000)
        winner = "NONE"
        
    mainSurface.fill(black)
    # events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    keys = pygame.key.get_pressed()
    
    if keys[K_UP]:
        player2Y -= 10
        ballserved = True
    if keys[K_DOWN]:
        player2Y += 10
        ballserved = True
    
    key_status = connexion.recv(1024).decode()
    
    if key_status == "UP":
        player1Y -= 10
        ballserved = True
    
    if key_status == "DOWN":
        player1Y += 10
        ballserved = True
    
    if player1Y <= 29:
        player1Y = 29
    if player1Y >= height-29:
        player1Y = height-29
        
    if player2Y <= 29:
        player2Y = 29
    if player2Y >= height-29:
        player2Y = height-29
        
    if ballserved:
        bx += sx
        by += sy
        ballRect.center = (bx, by)
        
    if (bx <= 0):
        player_score = 6 if player_score == 4 else player_score + 1
        bx, by = (width/2, (3*height/4) if (-1)**player_score > 0 else (height/4))
        sx, sy = (velocidad, velocidad)
        ballRect.center = (bx, by)
        ballserved = False
        player1Y = height/2
        player2Y = height/2
        batRect1.center = (player1X, player1Y)
        batRect2.center = (player2X, player2Y)
        sy *= (-1)**player_score
        
    if (bx >= width - 8):
        client_score = 6 if client_score == 4 else client_score + 1
        bx, by = (width/2, (3*height/4) if (-1)**client_score > 0 else (height/4))
        sx, sy = (-velocidad, velocidad)
        ballRect.center = (bx, by)
        ballserved = False
        player1Y = height/2
        player2Y = height/2
        batRect1.center = (player1X, player1Y)
        batRect2.center = (player2X, player2Y)
        sy *= (-1)**client_score
        
    if (by <= 0):
        by = 0
        sy *= -1
    if (by >= height - 8):
        by = 700 - 8
        sy *= -1
    
    if ballRect.colliderect(batRect1):
        bx = player1X + 12
        sx *= -1
        sy = (by-batRect1.center[1])/3
        obstacles = random_obstacle(1)
        
    if ballRect.colliderect(batRect2):
        bx = player2X - 12
        sx *= -1
        sy = (by-batRect2.center[1])/3
        obstacles = random_obstacle(0)
        
    if len(obstacles) > int(6 if dificultad == 6.5 else 10):
        del obstacles[0]
        
    obstacleHitIndex = ballRect.collidelist(obstacles)
    if obstacleHitIndex >= 0:
        hit_obs = obstacles[obstacleHitIndex]

        # Verificar colisión y cambiar dirección según el lado del obstáculo
        if (sx > 0 and bx - 8 < hit_obs.x) or (sx < 0 and bx + 8 > hit_obs.x + hit_obs.width):
            sx *= -1
        else:
            sy *= -1
        # Eliminar el obstáculo
        del obstacles[obstacleHitIndex]

    if player_score >= 5:
        client_score = 0
        player_score = 0
        player_sets += 1
        obstacles = []
        
    if client_score >= 5:
        client_score = 0
        player_score = 0
        client_sets += 1
        obstacles = []
        
    score_text = letra50.render(f"{client_score}       {player_score}", True, (200,200,200))
    sets_text = letra30.render(f"{client_sets}              {player_sets}", True, (200,200,200))
    
    batRect1.center = (player1X, player1Y)
    batRect2.center = (player2X, player2Y)
    
    for obs in obstacles:
        mainSurface.blit(obstacle, obs)
    mainSurface.blit(score_text, (425,50))
    mainSurface.blit(sets_text, (429,100))
    mainSurface.blit(ball, ballRect)
    mainSurface.blit(bat1, batRect1)
    mainSurface.blit(bat2, batRect2)
    pygame.draw.line(mainSurface,(255,255,255), (width/2, 0), (width/2, height))
    
    if player_sets == 3 or client_sets == 3:
        bx, by = (width/2, 3*height/4)
        sx, sy = (velocidad,velocidad)
        mainSurface.fill((0,0,0))
        if player_sets > client_sets:
            mainSurface.blit(texto_victoria,(width/2-100,height/2-50))
            winner = "HOST"
        else:
            mainSurface.blit(texto_derrota,(width/2-100,height/2-50))
            winner = "CLIENT"
        pygame.display.update()
        player_sets = 0
        client_sets = 0
    
    fpsClock.tick(60)
    pygame.display.update()