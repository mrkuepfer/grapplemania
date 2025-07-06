
import pygame as pg
import time
import math

def sqdist(p1, p2):
    """
    (point, point) -> float

    Returns the square of the distance between two points. More efficient than
    calculating the true distance; used for comparison.
    """
    return (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2

def dist(p1, p2):
    """
    (point, point) -> float

    Returns the true distance between two points. 
    """
    return sqdist(p1, p2)**0.5

class Player():

    def __init__(self, level, x, y, bounce=1):
        self.level = level
        self.radius = 30
        self.colour = "yellow"
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.futurex = 0
        self.futurey = 0
        self.grapple_range = 500
        self.bounce = bounce
        self.grapple = None
        self.checkpoints = []
        self.last_checkpoint = None
        self.time = 0
        self.start_time = time.perf_counter()

        if level.start:
            self.x, self.y = level.start.rect.center

    def reset(self):
        """
        Moves player to start block and resets all relevant values.
        """
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.futurex = 0
        self.futurey = 0
        self.grapple = None
        self.checkpoints = []
        self.last_checkpoint = None
        self.time = 0
        self.start_time = time.perf_counter()
        if self.level:
            if self.level.start:
                self.x, self.y = self.level.start.rect.center
                self.futurex, self.futurey = self.level.start.rect.center

    def respawn(self):
        """
        Moves player to last checkpoint, restoring the position and velocity of when the player
        reached the checkpoint. If no checkpoints were reached, resets the player to start.
        """
        
        if self.last_checkpoint:
            self.x, self.y = self.last_checkpoint["pos"]
            self.futurex, self.futurey = self.last_checkpoint["pos"]
            self.vx, self.vy = self.last_checkpoint["vel"]
            self.grapple = None
        else:
            self.reset()

    def render(self, screen, cam):
        pg.draw.circle(screen, self.colour, (self.x-cam.x, self.y-cam.y), self.radius)
        if self.grapple:
            pg.draw.line(screen, "white",
                         (self.x-cam.x, self.y-cam.y),
                         (self.grapple[0]-cam.x, self.grapple[1]-cam.y))
                    
    def update(self, keys):
        self.vy += 0.2

        if self.grapple:
            self.vx += 0.005*(self.grapple[0]-self.x)
            self.vy += 0.005*(self.grapple[1]-self.y)

        if keys[pg.K_a] and self.vx > -5:
            self.vx -= 0.5

        if keys[pg.K_d] and self.vx < 5:
            self.vx += 0.5
                    
        self.futurex = self.x + self.vx
        self.futurey = self.y + self.vy

        # Wall collision:

        # Get nearest block that collides with line between current and future position
        nearest_point = None
        nearest_block = None
        for block in self.level.walls:
            # Increase block size by ball radius to check
            # for collision with outside of ball
            collision_block = block.rect.inflate(2*self.radius, 2*self.radius)
            # Check if line between current and future position
            # intersects with rectangle
            collision_line = collision_block.clipline(self.x, self.y, self.futurex, self.futurey)
            if collision_line:
                point = collision_line[0]
                if (nearest_point == None or sqdist((self.x, self.y), point) < sqdist((self.x, self.y), nearest_point)):
                    nearest_point = point
                    nearest_block = collision_block

        if nearest_point:
            collision_x, collision_y = nearest_point
            # Bottom/right end of clipped line is off by one in Pygame's implemenation
            if self.vx < 0:
                collision_x += 1
            if self.vy < 0:
                collision_y += 1

            if nearest_block.left < collision_x < nearest_block.right:
                self.futurey = 2*collision_y-self.futurey
                self.vy *= -1*self.bounce
            if nearest_block.top < collision_y < nearest_block.bottom:
                self.futurex = 2*collision_x-self.futurex
                self.vx *= -1*self.bounce

        for booster in self.level.boosters:
            collision_block = booster.rect.inflate(2*self.radius, 2*self.radius)
            if collision_block.collidepoint(self.x, self.y):
                self.vx *= booster.strength
                self.vy *= booster.strength

        for checkpoint in self.level.checkpoints:
            collision_block = checkpoint.rect.inflate(2*self.radius, 2*self.radius)
            if collision_block.collidepoint(self.x, self.y) and checkpoint not in self.checkpoints:
                self.checkpoints.append(checkpoint)
                # Save velocity so it can be restored upon respawn
                self.last_checkpoint = {"pos": (self.x, self.y),
                                        "vel": (self.vx, self.vy)}

        for deathblock in self.level.deathblocks:
            collision_block = deathblock.rect.inflate(2*self.radius, 2*self.radius)
            if collision_block.collidepoint(self.x, self.y):
                self.respawn()

        for end in self.level.ends:
            collision_block = end.rect.inflate(2*self.radius, 2*self.radius)
            if collision_block.collidepoint(self.x, self.y) and len(self.checkpoints) == len(self.level.checkpoints):
                print("Finished the level in", self.time, "seconds.")
                self.reset()
                    
        self.x = self.futurex
        self.y = self.futurey

        self.time = time.perf_counter() - self.start_time

    def grapple_towards(self, point):
        """
        Sets the player's grapple location to the nearest point on the ray from the player
        passing through the given point, up to the player's maximum grapple range, that collides
        with a wall.
        """
        angle = math.atan2(point[1]-self.y, point[0]-self.x)
        max_grapple_x = self.x + self.grapple_range*math.cos(math.atan2(point[1]-self.y, point[0]-self.x))
        max_grapple_y = self.y + self.grapple_range*math.sin(math.atan2(point[1]-self.y, point[0]-self.x))

        # Find nearest colliding point with wall
        # Get nearest block that collides with line between current and future position
        nearest_point = None
        for wall in self.level.walls:
            collision_line = wall.rect.clipline(self.x, self.y, max_grapple_x, max_grapple_y)
            if collision_line:
                point = collision_line[0]
                if (nearest_point == None or sqdist((self.x, self.y), point) < sqdist((self.x, self.y), nearest_point)):
                    nearest_point = point
        self.grapple = nearest_point

    def jump(self):
        """
        Causes player to jump if a small rectangle below the player is colliding with a wall.
        """
        for b in self.level.walls:
            jump_rect = pg.Rect(self.x-10, self.y+self.radius, 20, 5)
            if b.rect.colliderect(jump_rect):
                self.vy -= 10
                break



