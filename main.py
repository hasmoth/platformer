import pygame, sys
from settings import *
from overworld import Overworld
from level import Level
from game_data import *

class Game:
    def __init__(self) -> None:
        self.level = None
        self.current_level = 0
        self.max_level = 0
        self.total_levels = len(levels)
        # overworld
        self.overworld = Overworld(self.current_level,self.max_level,screen,self.create_level)
        self.state = 'overworld'

    def create_level(self,current_level):
        self.level = Level(screen,levels[current_level],self.create_overword)
        self.state = 'level'

    def create_overword(self,success):
        if success and self.max_level < self.total_levels:
            self.max_level += 1
            self.current_level += 1

        self.overworld = Overworld(self.current_level,self.max_level,screen,self.create_level)
        self.state = 'overworld'

    def run(self):
        if self.state == 'level':
            self.level.run()
        elif self.state == 'overworld':
            self.overworld.run()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
pygame.display.set_caption('Pirates')
clock = pygame.time.Clock()
game = Game()
while True:
    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    game.run()
    pygame.display.update()
    clock.tick(FPS)