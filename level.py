import pygame as pg

# All coordinates must not be negative due to pygame's pixel rounding
# behaviour causing collision bugs

class Block:

    blocks = []

    def __init__(self, x, y, width, height, colour):
        if x < 0 or y < 0:
            raise ValueError("Block coordinates cannot be negative.")
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, width, height)
        self.colour = colour
        self.type = "block"
        Block.blocks.append(self)

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def render(self, screen, cam):
        drawn_rect = self.rect.move(-cam.x, -cam.y)
        pg.draw.rect(screen, self.colour, drawn_rect)


class WallBlock(Block):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "white")
        self.type = "wall"

class StartBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "green")
        self.type = "start"

class EndBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "red")
        self.type = "end"

class BoosterBlock(Block):

    def __init__(self, x, y, width, height, strength=1.05):
        super().__init__(x, y, width, height, "orange")
        self.type = "booster"
        self.strength = strength

class CheckpointBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "blue")
        self.type = "checkpoint"    

class DeathBlock(Block):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "darkmagenta")
        self.type = "death"

blocks = {"block": Block,
          "wall": WallBlock,
          "start": StartBlock,
          "end": EndBlock,
          "booster": BoosterBlock,
          "checkpoint": CheckpointBlock,
          "death": DeathBlock}

class Level:

    def __init__(self, fname=None):
        self.all_blocks = []
        self.start = None
        self.walls = []
        self.ends = []
        self.boosters = []
        self.checkpoints = []
        self.deathblocks = []
        self.blocktypes = {WallBlock: self.walls,
                           EndBlock: self.ends,
                           BoosterBlock: self.boosters,
                           CheckpointBlock: self.checkpoints,
                           DeathBlock: self.deathblocks}
        if fname:
            with open(fname) as file:
                lines = file.readlines()
                for line in lines:
                    vals = line.split()
                    t = vals[0]
                    if t in blocks:
                        BlockType = blocks[t]
                        self.add_block(BlockType(int(vals[1]), int(vals[2]), int(vals[3]), int(vals[4])))

    def add_block(self, block):
        if isinstance(block, StartBlock):
            self.start = block
            # Only one start allowed
            for b in self.all_blocks:
                if isinstance(b, StartBlock):
                    self.all_blocks.remove(b)
        else:
            for blocktype, blocklist in self.blocktypes.items():
                if isinstance(block, blocktype):
                    blocklist.append(block)
        self.all_blocks.append(block)

    def render(self, screen, cam):
        for o in self.all_blocks:
            o.render(screen, cam)

    def delete_block(self, block):
        while block in self.all_blocks:
            self.all_blocks.remove(block)
        for blocklist in self.blocktypes.values():
            while block in blocklist:
                blocklist.remove(block)

    def save_to_file(self, fname):
        with open(fname, 'w') as file:
            for b in self.all_blocks:
                s = " ".join([str(a) for a in [b.type, b.x, b.y, b.rect.width, b.rect.height, b.colour]])
                file.write(s+"\n")
