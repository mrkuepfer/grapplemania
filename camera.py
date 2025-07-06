# Camera

from constants import *
import pygame as pg

class Camera:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.tx = 0
        self.ty = 0

    def set_target(self, x, y):
        self.tx = x
        self.ty = y

    def update(self):
        self.x += (self.tx-SCREEN_WIDTH/2-self.x)*0.1
        self.y += (self.ty-SCREEN_HEIGHT/2-self.y)*0.1

    def get_mouse_world_pos(self):
        return (pg.mouse.get_pos()[0]+self.x, pg.mouse.get_pos()[1]+self.y)
        
