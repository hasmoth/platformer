import pygame
from settings import TILESIZE

from support import import_folder

class UI:
    def __init__(self,surface) -> None:
        self.display_surface = surface

        # health
        self.bar_parts = import_folder('../assets/Wood and Paper UI/Sprites/Life Bars/Big Bars/')
        self.bar_colors = import_folder('../assets/Wood and Paper UI/Sprites/Life Bars/Colors/')
        for part in range(0,len(self.bar_parts)):
            self.bar_parts[part] = pygame.transform.scale(self.bar_parts[part],(64,64))

        self.red_bar = pygame.transform.scale(self.bar_colors[0],(64,4))

        self.hp_bar = pygame.surface.Surface((4*TILESIZE,TILESIZE),flags = pygame.SRCALPHA)
        self.hp_bar.blit(self.bar_parts[0],(0,0))
        self.hp_bar.blit(self.bar_parts[2],(TILESIZE,0))
        self.hp_bar.blit(self.bar_parts[2],(2*TILESIZE,0))
        self.hp_bar.blit(self.bar_parts[3],(3*TILESIZE,0))

        self.bar_max = 214

        # coins
        self.coin = pygame.transform.scale(pygame.image.load('../assets/Pirate Treasure/Sprites/Silver Coin/01.png'),(32,32))
        self.coin_rect = self.coin.get_rect(topleft = (40,60))
        self.font = pygame.font.Font('../assets/joystix.ttf',25)

    def show_healthbar(self,current,max):
        if current == 0:
            self.hp_bar.blit(self.bar_parts[1],(0,0))
        self.display_surface.blit(self.hp_bar,(20,10))
        ratio = current / max
        current_width = ratio * self.bar_max if ratio >= 0 else 0
        self.display_surface.blit(pygame.transform.scale(self.red_bar,(current_width,4)),(53,38))

    def show_coins(self,num_coins):
        self.display_surface.blit(self.coin,self.coin_rect)
        coin_amount_surf = self.font.render(str(num_coins),False,'#33323d')
        coin_amount_rect = coin_amount_surf.get_rect(midleft = (self.coin_rect.right + 5,self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surf,coin_amount_rect)