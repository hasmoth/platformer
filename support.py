import pygame
from csv import reader
from os import walk
from tkinter import image_names

from settings import SPRITESIZE

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map,delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

    # dictionary = {
    #   'style': import_csv_layout('path/to/file.csv')
    # }

def import_folder(path,scale=(0,0)):
    surface_list = []

    for _,__,img_files in walk(path):
        for img in sorted(img_files):
            full_path = path + '/' + img
            img_surf = pygame.image.load(full_path).convert_alpha()
            if scale[0] and scale[1]:
                img_size = img_surf.get_size()
                size_x = img_size[0] * scale[0]
                size_y = img_size[1] * scale[1]
                img_surf = pygame.transform.scale(img_surf,(size_x,size_y))
            surface_list.append(img_surf)

    return surface_list


    # dictionary = {
    #   'style': import_folder('path/to/file')
    # }

def import_from_sprite_sheet(path,spritesize=(SPRITESIZE,SPRITESIZE)):
    sprite_sheet = pygame.image.load(path).convert_alpha()
    num_col = int(sprite_sheet.get_size()[0] / spritesize[0])
    num_row = int(sprite_sheet.get_size()[1] / spritesize[1])

    sprites = []
    for row in range(num_row):
        for col in range(num_col):
            x = col * spritesize[0]
            y = row * spritesize[1]
            surface = pygame.Surface(spritesize,flags = pygame.SRCALPHA)
            surface.blit(sprite_sheet,(0,0),pygame.Rect(x,y,spritesize[0],spritesize[1]))
            sprites.append(surface)

    return sprites


class Direction:
    def __init__(self) -> None:
        self.vector = pygame.math.Vector2(0,0)
        self.facing_right = True

    def __mul__(self,rhs):
        if isinstance(rhs,int) or isinstance(rhs,float):
            self.vector.x *= rhs
            self.vector.y *= rhs

            return self.vector
        else:
            raise TypeError("unsupported operand type(s) for *: '{}' and '{}'").format(self.__class__, type(rhs))

    def right(self):
        self.vector.x = 1
        self.facing_right = True

    def left(self):
        self.vector.x = -1
        self.facing_right = False

    def is_up(self):
        return self.vector.y < 0

    def is_down(self):
        return self.vector.y > 1

    def get(self):
        return self.vector.length() if self.vector.x != 0 and self.vector.y != 0 else 0