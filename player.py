from math import sin
import pygame

from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self,pos,surface,jump_sound) -> None:
        super(Player,self).__init__()

        self.display_surface = surface

        # graphics
        self.animations = None
        self.dust_particles = None
        self.import_player_assets()

        # animations
        self.frame_index = 0
        self.dust_index = 0
        self.animation_speed = ANIMATIONSPEED

        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = pygame.Rect(self.rect.left + 2,self.rect.top,42,56)
        self.direction = Direction()
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -16
        self.player_jump_sound = jump_sound

        # player status
        self.status = 'idle' # ['idle','jump','fall','run']
        self.landed = False
        self.death = False
        self.hit_death = False

        # collision status
        self.collisions = {
            'left': False,
            'right': False,
            'top': False,
            'bottom': False,
        }

        # player stats
        self.lives = 3
        self.hp = 250
        self.hp_max = 500
        self.coins = 0

        self.invincible = False
        self.invincibility_duration = 200
        self.hurt_time = 0

    # movement assests and dust assets
    def import_player_assets(self):
        # movement assets
        character_path = '../assets/Captain_Clown_Nose/with_sword/'
        self.animations = {'idle': [],
                           'run': [],
                           'jump': [],
                           'fall': [],
                           'dead_ground': []}
        # self.animations = {'idle': [],
        #                    'run': [],
        #                    'jump': [],
        #                    'fall': [],
        #                    'hit': [],
        #                    'dead_hit': [],
        #                    'dead_ground': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
            for idx in range(0,len(self.animations[animation])):
                surface = pygame.Surface((37,28),flags = pygame.SRCALPHA)
                surface.blit(self.animations[animation][idx],(-20,-4))
                self.animations[animation][idx] = pygame.transform.scale(surface,(74,56))

        # dust assets
        dust_path = '../assets/Captain_Clown_Nose/Dust_Particles/'
        self.dust_particles = {'run': [],
                               'jump': [],
                               'land': []}

        for dust in self.dust_particles.keys():
            full_path = dust_path + dust
            self.dust_particles[dust] = import_folder(full_path)

    # player input
    def get_input(self):
        keys = pygame.key.get_pressed()
        # no imput when player is dead
        if self.hp > 0:
            # up/down
            if keys[pygame.K_UP]:
                pass
            elif keys[pygame.K_DOWN]:
                pass

            # left/right
            if keys[pygame.K_LEFT]:
                self.direction.left()
            elif keys[pygame.K_RIGHT]:
                self.direction.right()
            else:
                self.direction.vector.x = 0

            # jump
            if keys[pygame.K_SPACE] and self.collisions['bottom']:
                self.player_jump_sound.play()
                self.jump()

        # attack
        if keys[pygame.K_LCTRL]:
            pass

    # set status based on direction
    def get_status(self):
        if self.death:
            self.status = 'dead_ground'
        else:
            if self.direction.is_up():
                self.status = 'jump'
            elif self.direction.is_down():
                self.status = 'fall'
            else:
                if self.status == 'fall':
                    self.landed = True
                if self.direction.vector.x != 0:
                    self.status = 'run'
                else:
                    self.status = 'idle'

    # animate movement
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(bottomleft = (self.hitbox.left - 2, self.hitbox.bottom))
        # if player is facing left we just flip the image
        if not self.direction.facing_right:
            self.image = pygame.transform.flip(self.image,True,False)
            self.rect = self.image.get_rect(bottomright = (self.hitbox.right - 2, self.hitbox.bottom))

        # respect collisions
        if self.collisions['left'] and self.collisions['bottom']:
            self.rect = self.image.get_rect(bottomright = (self.hitbox.right - 2, self.hitbox.bottom))
        elif self.collisions['right'] and self.collisions['bottom']:
            self.rect = self.image.get_rect(bottomleft = (self.hitbox.left + 2, self.hitbox.bottom))
        elif self.collisions['bottom']:
            pass
            #self.rect = self.image.get_rect(bottomleft = (self.hitbox.left + 2, self.hitbox.bottom))
        elif self.collisions['left'] and self.collisions['top']:
            self.rect = self.image.get_rect(topright = (self.hitbox.right -2 , self.hitbox.top))
        elif self.collisions['right'] and self.collisions['top']:
            self.rect = self.image.get_rect(topleft = (self.hitbox.left + 2, self.hitbox.top ))
        elif self.collisions['top']:
            self.rect = self.image.get_rect(midtop = self.hitbox.midtop)

        if self.invincible or self.hp <= 0:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    # make dust particles
    def play_dust_animation(self):
        if self.status == 'run' or self.status == 'jump' or self.landed:
            status = self.status
            if self.landed: status = 'land'
            dust = self.dust_particles[status]

            if len(dust):
                self.dust_index += self.animation_speed

                if self.dust_index >= len(dust):
                    self.dust_index = 0

                dust_img = pygame.transform.scale(dust[int(self.dust_index)],(104,40))

                if status == 'run':
                    if self.direction.facing_right:
                        pos = self.hitbox.midbottom - pygame.math.Vector2(60,37)
                    else:
                        pos = self.hitbox.midbottom - pygame.math.Vector2(30,37)
                        dust_img = pygame.transform.flip(dust_img,True,False)
                    self.display_surface.blit(dust_img,pos)
                elif status == 'jump':
                    pos = self.hitbox.midtop - pygame.math.Vector2(dust_img.get_size()[0]/2,-20)
                    self.display_surface.blit(dust_img,pos)
                elif status == 'land':
                    # play complete landing animation
                    pos = self.hitbox.midtop - pygame.math.Vector2(dust_img.get_size()[0]/2,-18)
                    self.dust_index = 0
                    while self.dust_index < len(dust) - 1:
                        self.dust_index += self.animation_speed
                        dust_img = pygame.transform.scale(dust[int(self.dust_index)],(104,40))
                        self.display_surface.blit(dust_img,pos)

                    self.landed = False
                    self.play_dust_animation()

    # death by falling
    def play_death_animation(self):
        self.direction.vector.x = 0
        self.hp = 0
        self.jump()
        self.death = True

        return self.initial_jump_y

    # initiate jump
    def jump(self):
        self.dust_index = 0
        self.initial_jump_y = self.direction.vector.y
        self.direction.vector.y = self.jump_speed

    # make player fall
    def apply_gravity(self):
        self.direction.vector.y += self.gravity
        self.hitbox.y += self.direction.vector.y
        self.rect.y = self.hitbox.y

    # flicker
    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    # reduce hp
    def take_damage(self):
        if not self.invincible:
            self.hp -= 10
            self.hurt_time = pygame.time.get_ticks()
            self.invincible = True

    # make player invincible
    def invincibility_timer(self):
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.hurt_time > self.invincibility_duration:
                self.invincible = False

    # from Sprite
    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        self.play_dust_animation()
        self.invincibility_timer()



