#########################################

# Grapple racing game

#########################################

import level
import camera
import client
import pygame as pg
import threading
import time

from player import Player
from level import Level
from constants import *

mode = input("[O]nline or [s]ingleplayer mode: ").lower()
if mode == "o":
    ip = input("Host IP: ")
    port = int(input("Host port: "))
    conn = client.Connection(ip, port)
    level = conn.level
else:
    level = Level(SAVES_FOLDER + input("Level name: ")+ SAVES_EXT)

# Setup pygame and game objects
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SCALED)
background = pg.Surface(screen.get_size())
font = pg.font.SysFont("Courier", 30)

camera = camera.Camera()

def debug_print():
    """
    Utility function for debugging. Called by pressing 'p' ingame.
    """
    print(level.walls)
    
def dist(x1, y1, x2, y2):
    return ((x2-x1)**2+(y2-y1)**2)**0.5

player = Player(level, 500, 200, 0.2)


running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            player.grapple_towards((event.pos[0]+camera.x, event.pos[1]+camera.y))
        if event.type == pg.MOUSEBUTTONUP:
            player.grapple = None
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                player.jump()
            if event.key == pg.K_p:
                debug_print()
            if event.key == pg.K_r:
                player.reset()
            if event.key == pg.K_f:
                player.respawn()

             
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Update everything
    keys = pg.key.get_pressed()
    player.update(keys)
    camera.set_target(player.x, player.y)
    camera.update()

    # Send/recieve updates from server in separate thread
    if mode == 'o':
        network_thread = threading.Thread(target=conn.update, args=(player,), daemon=True)
        network_thread.start()

    # Render everything
    level.render(screen, camera)
    player.render(screen, camera)
    if mode == 'o':
        for ip, p in conn.players.items():
            if ip != conn.ip:
                p.render(screen, camera)

    # Render time, checkpoint progress in top left corner of screen
    time_text = font.render("{:.3f}".format(player.time), True, "white")
    time_rect = time_text.get_rect()
    time_rect.x = 0
    time_rect.y = 0
    cps_text = font.render(str(len(player.checkpoints)) + "/" + str(len(level.checkpoints)), True, "white")
    cps_rect = cps_text.get_rect()
    cps_rect.x = time_rect.width + 20
    cps_rect.y = 0
    pg.draw.rect(screen, "black", time_rect.union(cps_rect)) # Text background
    screen.blit(time_text, time_rect)
    screen.blit(cps_text, cps_rect)
    
    # flip() the display to update your work on screen
    pg.display.flip()

    clock.tick(60) # limits FPS to 60

# Quit the game and do any necessary shutdown actions
pg.quit()
