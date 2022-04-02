from random import randint
import pygame
from background import Sky, Water
from player import Player
from settings import SCREENHEIGHT, SCREENWIDTH, TILESIZE
from support import *
from tiles import Tile, StaticTile, Coin, Palm, Goal
from enemy import Enemy
from ui import UI


class Level:
    def __init__(self,display_surface,level_data,create_overworld) -> None:
        self.display_surface = display_surface
        self.world_shift = 0
        self.current_x = None
        self.level_data = level_data
        self.create_overworld = create_overworld

        # sounds
        self.player_jump_sound = pygame.mixer.Sound('../assets/sounds/jump.wav')
        self.player_hit_sound = pygame.mixer.Sound('../assets/sounds/hit.wav')
        self.player_stomp_sound = pygame.mixer.Sound('../assets/sounds/stomp.wav')
        self.player_death_sound = pygame.mixer.Sound('../assets/sounds/death.wav')
        self.coin_sound = pygame.mixer.Sound('../assets/sounds/coin.wav')

        self.player_jump_sound.set_volume(0.2)
        self.player_hit_sound.set_volume(0.2)
        self.player_stomp_sound.set_volume(0.2)
        self.coin_sound.set_volume(0.2)
        self.player_death_sound.set_volume(0.3)

        self.death_channel = pygame.mixer.Channel(1)
        self.MUSIC_END = pygame.USEREVENT+1
        self.death_channel.set_endevent(self.MUSIC_END)

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # user interface
        self.ui = UI(self.display_surface)

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # terrain etc.
        self.sprite_groups = {}.fromkeys(level_data.keys(),0) # {key: sprite_group}
        for key in level_data.keys():
            if key != 'player' and key != 'node_position' and key != 'node_path':
                layout = import_csv_layout(level_data[key])
                if key == 'terrain':
                    self.level_width = len(layout[0])
                self.sprite_groups[key] = self.create_tile_group(layout,key)

        # sky, water, clouds
        self.sky = Sky(8)
        self.water = Water(self.level_width*TILESIZE)
        self.clouds = None

    # get player starting and level goal positions
    def player_setup(self,layout):
        for row_idx, row in enumerate(layout):
            for col_idx, val in enumerate(row):
                if val != '-1':
                    x = col_idx * TILESIZE
                    y = row_idx * TILESIZE
                    if val == '0': # player starting position
                        sprite = Player((x,y),self.display_surface,self.player_jump_sound)
                        self.player.add(sprite)
                    if val == '1': # level goal position
                        sprite = Goal(TILESIZE,(x,y),'../assets/Pirate Treasure/Sprites/Small Maps/Small Map 4/')
                        self.goal.add(sprite)

    # return sprite groups for each level element
    def create_tile_group(self,layout,key):
        sprite_group = pygame.sprite.Group()
        sprite = None
        for row_idx,row in enumerate(layout):
            for col_idx,val in enumerate(row):
                if val != '-1':
                    pos = (col_idx*TILESIZE,row_idx*TILESIZE)

                    if key == 'terrain':
                        terrain_list = import_from_sprite_sheet('../assets/2 - Level/graphics/terrain/terrain_tiles.png')
                        surface = terrain_list[int(val)]
                        sprite = StaticTile(TILESIZE,pos,surface)
                    if key == 'grass':
                        pass
                    if key == 'crates':
                        surface = pygame.image.load('../assets/2 - Level/graphics/terrain/crate.png').convert_alpha()
                        sprite = StaticTile(TILESIZE,(pos[0],pos[1] + 22),surface)
                    if key == 'coins':
                        if val == '0': sprite = Coin(TILESIZE,pos,'../assets/2 - Level/graphics/coins/gold',2)
                        if val == '1': sprite = Coin(TILESIZE,pos,'../assets/2 - Level/graphics/coins/silver',1)
                    if key == 'fg palms':
                        if val == '0': sprite = Palm(TILESIZE,pos,'../assets/2 - Level/graphics/terrain/palm_small', 38)
                        if val == '1': sprite = Palm(TILESIZE,pos,'../assets/2 - Level/graphics/terrain/palm_large', 70)
                    if key == 'bg palms':
                        sprite = Palm(TILESIZE,pos,'../assets/2 - Level/graphics/terrain/palm_bg', 64)
                    if key == 'enemies':
                        sprite = Enemy(TILESIZE,pos,'../assets/The Crusty Crew/Sprites/Fierce Tooth/idle')
                    if key == 'constraints':
                        sprite = Tile(TILESIZE,pos)

                    if sprite:
                        sprite_group.add(sprite)
                    sprite = None

        return sprite_group

    # horizontal player movement and collisions
    def horizontal_player_movement(self):
        player = self.player.sprite
        player.hitbox.x += player.direction.vector.x * player.speed
        collidable_sprites = self.sprite_groups['terrain'].sprites() + self.sprite_groups['crates'].sprites() + self.sprite_groups['fg palms'].sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.hitbox):
                if player.direction.vector.x > 0:
                    player.hitbox.right = sprite.rect.left
                    self.current_x = player.hitbox.right
                    player.collisions['right'] = True
                elif player.direction.vector.x < 0:
                    player.hitbox.left = sprite.rect.right
                    self.current_x = player.hitbox.left
                    player.collisions['left'] = True

        if player.collisions['left'] and (player.hitbox.left < self.current_x or player.direction.vector.x >= 0):
            player.collisions['left'] = False
        if player.collisions['right'] and (player.hitbox.right > self.current_x or player.direction.vector.x <= 0):
            player.collisions['right'] = False

    # vertical player movement and collisions
    def vertical_player_movement(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.sprite_groups['terrain'].sprites() + self.sprite_groups['crates'].sprites() + self.sprite_groups['fg palms'].sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.hitbox):
                if player.direction.vector.y > 0:
                    player.hitbox.bottom = sprite.rect.top
                    player.direction.vector.y = 0
                    player.collisions['bottom'] = True
                elif player.direction.vector.y < 0:
                    player.hitbox.top = sprite.rect.bottom
                    player.direction.vector.y = 0
                    player.collisions['top'] = True

        if player.collisions['bottom'] and player.direction.is_down() or player.direction.is_up():
            player.collisions['bottom'] = False
        if player.collisions['top'] and player.direction.vector.y > 0.1:
            player.collisions['top'] = False

    # player camera
    def scroll_x(self):
        player = self.player.sprite
        player_x = player.hitbox.centerx
        direction_x = player.direction.vector.x

        if player_x < SCREENWIDTH / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > SCREENWIDTH - (SCREENWIDTH / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    # collect coins
    def coin_collisions(self):
        player = self.player.sprite
        for coin in self.sprite_groups['coins']:
            if coin.rect.colliderect(player.hitbox):
                self.coin_sound.play()
                player.coins += coin.value
                coin.kill()

    # enemy attack or player attack
    def enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite,self.sprite_groups['enemies'],False)
        if enemy_collisions:
            for enemy in enemy_collisions:
                # pygame.draw.rect(self.display_surface,'black',enemy.rect,1)
                if enemy.rect.top < self.player.sprite.rect.bottom < enemy.rect.centery and self.player.sprite.direction.vector.y >= 0:
                    self.player_stomp_sound.play()
                    self.player.sprite.direction.vector.y = -15
                    enemy.kill()
                else:
                    self.player_hit_sound.play()
                    self.player.sprite.take_damage()

    def enemy_constraints_collisions(self):
        for enemy in self.sprite_groups['enemies']:
            if pygame.sprite.spritecollide(enemy,self.sprite_groups['constraints'],False):
                enemy.reverse()

    # reached level goal
    def goal_collision(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,True):
            # play_win_animation
            self.create_overworld(True)

    # fall death
    def check_player_fall_death(self):
        if self.player.sprite.rect.top > SCREENHEIGHT and self.player.sprite.status != 'dead_ground':
            self.player.sprite.play_death_animation()
            self.player_death_sound.play()

    # death by 0 hp
    def check_player_hp_death(self):
        if self.player.sprite.hp <= 0 and self.player.sprite.status != 'dead_ground':
            self.player.sprite.play_death_animation()
            self.player_death_sound.play()

    # get back to overworld
    def check_overworld_condition(self):
        for event in pygame.event.get():
            if event.type == self.MUSIC_END and self.player.sprite.hp == 0:
                self.create_overworld(False)

    def run(self):
        self.sky.draw(self.display_surface)

        # terrain bg
        self.sprite_groups['bg palms'].update(self.world_shift)
        self.sprite_groups['bg palms'].draw(self.display_surface)

        self.sprite_groups['terrain'].update(self.world_shift)
        self.sprite_groups['terrain'].draw(self.display_surface)

        self.sprite_groups['crates'].update(self.world_shift)
        self.sprite_groups['crates'].draw(self.display_surface)

        self.sprite_groups['coins'].update(self.world_shift)
        self.sprite_groups['coins'].draw(self.display_surface)

        # enemies
        self.sprite_groups['enemies'].update(self.world_shift)
        self.sprite_groups['constraints'].update(self.world_shift)
        self.enemy_constraints_collisions()

        self.sprite_groups['enemies'].draw(self.display_surface)

        # terrain fg
        self.sprite_groups['fg palms'].update(self.world_shift)
        self.sprite_groups['fg palms'].draw(self.display_surface)

        # water
        self.water.draw(self.display_surface,self.world_shift)

        # goal
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        # dust
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        # player
        self.player.update()
        self.horizontal_player_movement()
        self.vertical_player_movement()
        self.coin_collisions()
        self.enemy_collisions()
        self.scroll_x()
        # pygame.draw.rect(self.display_surface,'black',self.player.sprite.rect,1)
        # pygame.draw.rect(self.display_surface,'red',self.player.sprite.hitbox,1)
        self.player.draw(self.display_surface)
        # death
        self.check_player_fall_death()
        self.check_player_hp_death()

        # ui
        self.ui.show_healthbar(self.player.sprite.hp,self.player.sprite.hp_max)
        self.ui.show_coins(self.player.sprite.coins)
        # win
        self.goal_collision()
        # go back to overworld
        self.check_overworld_condition()

