import pygame
from random import randint
from tiles import AnimatedTile

class Enemy(AnimatedTile):
    def __init__(self, size, pos, path) -> None:
        super().__init__(size, pos, path)

        self.speed = randint(1,3)

        # fondle surface
        for idx in range(0,len(self.frames)):
            surface = pygame.Surface((23,23),flags = pygame.SRCALPHA)
            surface.blit(self.frames[idx],(-7,-5))
            self.frames[idx] = pygame.transform.scale(surface,(46,46))
        self.rect = self.frames[0].get_rect(topleft = (pos[0],pos[1]+20))

    def flip_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def move(self):
        self.rect.x += self.speed

    def update(self, shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.flip_image()

