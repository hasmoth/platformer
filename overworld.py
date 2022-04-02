import pygame
from background import Sky
from game_data import levels
from support import import_folder
from settings import *
from tiles import AnimatedTile

class Node(AnimatedTile):
    def __init__(self, size, pos, path, locked) -> None:
        super().__init__(size, pos, path)
        self.locked = locked
        self.rect = self.image.get_rect(center = pos)

    def update(self):
        if self.locked:
            pass
        else:
            self.animate()

class Overworld:
    def __init__(self,current_level,max_level,surface,create_level) -> None:
        self.display_surface = surface
        self.current_level = current_level
        self.max_level = max_level
        self.create_level = create_level

        self.setup_nodes()
        self.sky = Sky(8)

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        for idx, node in enumerate(levels.values()):
            locked = idx > self.max_level
            sprite = Node(TILESIZE,node['node_position'],node['node_path'],locked)

            self.nodes.add(sprite)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.current_level > 0:
                self.current_level -= 1
        if keys[pygame.K_RIGHT]:
            if self.current_level < self.max_level:
                self.current_level += 1
        if keys[pygame.K_SPACE]:
            self.create_level(self.current_level)

    def run(self):
        self.sky.draw(self.display_surface)
        self.input()
        self.nodes.update()
        self.nodes.draw(self.display_surface)