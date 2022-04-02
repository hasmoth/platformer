import pygame
from settings import *
from support import import_folder

# basic tile
class Tile(pygame.sprite.Sprite):
    def __init__(self,size,pos) -> None:
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = pos)

    # from Sprite
    def update(self,shift):
        self.rect.x += shift

# static tile
class StaticTile(Tile):
    def __init__(self,size,pos,surface) -> None:
        super().__init__(size,pos)
        self.image = surface

# animated tile
class AnimatedTile(Tile):
    def __init__(self,size,pos,path) -> None:
        super().__init__(size,pos)
        self.frames = import_folder(path)

        self.frame_index = 0
        self.animation_speed = ANIMATIONSPEED
        self.image = self.frames[int(self.frame_index)]

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    # from Sprite
    def update(self,shift):
        self.animate()
        self.rect.x += shift

### specific Tile classes
# coin
class Coin(AnimatedTile):
    def __init__(self, size, pos, path, value) -> None:
        super().__init__(size, pos, path)
        center_x = pos[0] + int(size/2)
        center_y = pos[1] + int(size/2)
        self.rect = self.image.get_rect(center = (center_x,center_y))
        self.value = value
# animated palm
class Palm(AnimatedTile):
    def __init__(self, size, pos, path, offset) -> None:
        super().__init__(size, pos, path)
        self.rect.topleft = (pos[0],pos[1]-offset)
# goal map
class Goal(AnimatedTile):
    def __init__(self, size, pos, path) -> None:
        super().__init__(size, pos, path)
        for idx in range(0,len(self.frames)):
            self.frames[idx] = pygame.transform.scale(self.frames[idx],(38,38))
