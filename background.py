import pygame
from settings import *
from support import import_folder
from tiles import AnimatedTile

class Sky:
    def __init__(self,horizon) -> None:
        self.image = pygame.image.load('../assets/Palm Tree Island/Sprites/Background/BG Image.png').convert_alpha()
        # horizon is the upper third of the image
        horizon_y = horizon * TILESIZE
        self.image = pygame.transform.scale(self.image,(SCREENWIDTH,horizon_y*3))


    def draw(self,surface):
        surface.blit(self.image,(0,0))

class Water:
    def __init__(self,level_width) -> None:
        water_start = -SCREENWIDTH
        img_width = 96
        tile_num = int((level_width + SCREENWIDTH * 2) / img_width)
        self.water_sprites = pygame.sprite.Group()
        for tile in range(tile_num):
            pos = (tile * img_width + water_start,SCREENHEIGHT - 30)
            sprite = AnimatedTile(img_width,pos,'../assets/Merchant Ship/Sprites/Water/Water/Top')
            self.water_sprites.add(sprite)

    def draw(self,surface,shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)