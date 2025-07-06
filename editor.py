# Editor

import camera
import pygame as pg

from level import *
from constants import *

level_file = input("Enter file to load, or 'n' for new level: ")
if level_file == 'n':
    level = Level()
else:
    level = Level(SAVES_FOLDER + level_file + SAVES_EXT)


# Setup pygame and game objects
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SCALED)
font = pg.font.SysFont("Courier", 30)


block_types = {pg.K_1: {"type": WallBlock, "colour": "grey"},
               pg.K_2: {"type": StartBlock, "colour": "dark green"},
               pg.K_3: {"type": EndBlock, "colour": "dark red"},
               pg.K_4: {"type": BoosterBlock, "colour": "dark orange"},
               pg.K_5: {"type": CheckpointBlock, "colour": "blue"},
               pg.K_6: {"type": DeathBlock, "colour": "dark magenta"}}

GRID_SIZE = 20
selected_block = Block(0, 0, 2*GRID_SIZE, 2*GRID_SIZE, 'grey')
selected_type = WallBlock
grid_mode = False

camera = camera.Camera()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.mouse.get_pressed()[0]:
                new = selected_type(selected_block.x,
                                    selected_block.y,
                                    selected_block.rect.width,
                                    selected_block.rect.height)
                level.add_block(new)
            if pg.mouse.get_pressed()[2]:
                for b in level.all_blocks:
                    if b.rect.collidepoint(camera.get_mouse_world_pos()):
                        level.delete_block(b)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r: # Rotate block               
                tmp = selected_block.rect.width
                selected_block.rect.width = selected_block.rect.height
                selected_block.rect.height = tmp
            if event.key == pg.K_g:
                grid_mode = not grid_mode
            if grid_mode:
                # Block size controls
                if event.key == pg.K_a:
                    selected_block.rect.width = max(GRID_SIZE, selected_block.rect.width-GRID_SIZE)
                if event.key == pg.K_s:
                    selected_block.rect.width += GRID_SIZE
                if event.key == pg.K_z:
                    selected_block.rect.height = max(GRID_SIZE, selected_block.rect.height-GRID_SIZE)
                if event.key == pg.K_x:
                    selected_block.rect.height += GRID_SIZE
                # Camera controls
                if event.key == pg.K_RIGHT:
                    camera.x += GRID_SIZE*speed
                if event.key == pg.K_LEFT:
                    camera.x = max(0, camera.x-GRID_SIZE*speed)
                if event.key == pg.K_DOWN:
                    camera.y += GRID_SIZE*speed
                if event.key == pg.K_UP:
                    camera.y = max(0, camera.y-GRID_SIZE*speed)
            for k, vals in block_types.items():
                if event.key == k:
                    selected_block.colour = vals["colour"]
                    selected_type = vals["type"]
            
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Update game
    if grid_mode:
        selected_block.x = ((pg.mouse.get_pos()[0]) // GRID_SIZE)*GRID_SIZE+camera.x
        selected_block.y = ((pg.mouse.get_pos()[1]) // GRID_SIZE)*GRID_SIZE+camera.y
    else:
        selected_block.x = pg.mouse.get_pos()[0] + camera.x
        selected_block.y = pg.mouse.get_pos()[1] + camera.y
    selected_block.update()
    keys = pg.key.get_pressed()
    if keys[pg.K_LSHIFT]:
        speed = 5
    else:
        speed = 2
    if not grid_mode:
        # Block size controls
        if keys[pg.K_a]:
            selected_block.rect.width = max(1, selected_block.rect.width-speed)
        if keys[pg.K_s]:
            selected_block.rect.width += speed
        if keys[pg.K_z]:
            selected_block.rect.height = max(1, selected_block.rect.height-speed)
        if keys[pg.K_x]:
            selected_block.rect.height += speed
    
        # Camera controls
        if keys[pg.K_RIGHT]:
            camera.x += speed
        if keys[pg.K_LEFT] and camera.x >= speed:
            camera.x = max(0, camera.x - speed)
        if keys[pg.K_UP] and camera.y >= speed:
            camera.y = max(0, camera.y - speed)
        if keys[pg.K_DOWN]:
            camera.y += speed
 
    # Render game
    selected_block.render(screen, camera)
    level.render(screen, camera)

    # Show camera coords
    pg.draw.rect(screen, "black", (0, 0, 150, 30))
    coords_text = font.render(str((camera.x, camera.y)), True, "white")
    coords_rect = coords_text.get_rect()
    coords_rect.x = 0
    coords_rect.y = 0
    screen.blit(coords_text, coords_rect)

    # flip() the display to update your work on screen
    pg.display.flip()

    clock.tick(60) # limits FPS to 60

# Quit the game and do any necessary shutdown actions
pg.quit()

save_file = input("Enter name of save, or 'd' to discard: ")
if save_file != 'd':
    level.save_to_file(SAVES_FOLDER + save_file + SAVES_EXT)
