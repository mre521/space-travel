#
# game.py - core game functionality
#
# Space Travel
#     Copyright (C) 2014  Eric Eveleigh
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


import math
import random

import pygame.draw

from vector import Vector2D
from physics import Object2D

import entity
import physics

    
STAR_VELOCITY = -2000
STAR_SIZE = 6.0
class StarField(object):
    class Star(object):
        def __init__(self):
            self.position = Vector2D()
            self.velocity = Vector2D()
            self.size = 3.0
            self.color = (255,255,255)
            
        def get_position(self):
            return self.position
        
        def get_position_horiz(self):
            return self.position.get_x()
        
        def set_position_horiz(self, x):
            self.position.set_x(x)
            
        def set_position_vert(self, y):
            self.position.set_y(y)
            
        def set_velocity_horiz(self, x):
            self.velocity.set_x(x)
            
        def set_velocity_vert(self, x):
            self.velocity.set_x(x)
        
        def set_velocity(self, velocity):
            self.velocity.set_vect(velocity)
            
        def set_size(self, size):
            self.size = size
     
        def get_size(self):
            return self.size
        
        def set_color(self, color):
            self.color = color
            
        def get_color(self):
            return self.color
         
        def update(self, dt):
            self.position.add(self.velocity.scaled(dt))
            
    def __init__(self, width, height, num_stars):
        self.width = width
        self.height = height
        self.num_stars = num_stars
        
        self.star_velocity = STAR_VELOCITY
        
        
        '''
        Create the initial field
        '''
        self.stars = [] # raises exceptions when removed
        i = 0
        while i < self.num_stars:
            star = StarField.Star()
            self.distribute_horiz(star)
            self.distribute_vert(star)
            self.stars.append(star)
            i += 1
    
    def distribute_vert(self, star):
        '''
        Vertically position a star pseudo-randomly;
        Gaussian distributed.
        '''
        
        factor = float('inf') # something where fabs(factor) is > 1.0 basically
        
        '''
        The while loop is important to ensure 
        that |factor| <= 1.0 (star on the screen)
        '''
        while math.fabs(factor) > 1.0:
            factor = random.gauss(0.0, 0.75)
            
        vertical = (factor * self.height/2) + self.height/2
            
        velocity = (1.0-math.fabs(factor)) * self.star_velocity
        
        star.set_size((1.0-math.fabs(factor)) * STAR_SIZE)
        
        star.set_position_vert(vertical)
        star.set_velocity(Vector2D(velocity, 0))
    
    def distribute_horiz(self, star):
        horiz = random.random()*self.width
    
        star.set_position_horiz(horiz)
        
    def random_color(self, star):
        color = lambda: int(127 + random.random()*128)
        r = color()
        g = color()
        b = color()
        
        star.set_color((r,g,b))
        
    def wrap_star(self, star):
        star.set_position_horiz(self.width)
        self.distribute_vert(star)
        self.random_color(star)
        
    def update(self, dt):
        for star in self.stars:
            star.update(dt)
            if star.get_position_horiz() < 0:
                self.wrap_star(star)
            
    def draw(self, surface):
        for star in self.stars:
            pos = star.get_position().get_int()
            pygame.draw.circle(surface, star.get_color(), pos, int(star.get_size()), 0)
    
        
GAME_DIFF_EASY = 1
GAME_DIFF_MEDIUM = 2
GAME_DIFF_HARD = 3
GAME_SETTINGS_EASY = {'distance': 1200, 'default_regens': 5, 'default_hp': 100, 'aster_prob': 1.0/5, 'hole_prob': 1.0/20, 'shield_prob': 1.0/10, 'weapon_prob': 1.0/20}
GAME_SETTINGS_MEDIUM = {'distance': 2400, 'default_regens': 3, 'default_hp': 100, 'aster_prob': 1.0/4, 'hole_prob': 1.0/15, 'shield_prob': 1.0/15, 'weapon_prob': 1.0/25}
GAME_SETTINGS_HARD = {'distance': 4800, 'default_regens': 2, 'default_hp': 100, 'aster_prob': 1.0/3, 'hole_prob': 1.0/10, 'shield_prob': 1.0/20, 'weapon_prob': 1.0/30 }
GAME_MODE_NORMAL = 1
GAME_MODE_ENDURANCE = 2
GAME_TRAVEL_VELOCITY = 10.0 # 10 units of distance per second
GAME_SPAWN_PERIOD = 1.0 # spawn potential every second
class Game(object):
    '''
    The whole reason for creating every other class.
    '''
    class Settings(object):
        '''
        Helper for Game settings.
        '''
        def __init__(self, settings):
            self.add(settings)
                
        def add(self, settings):
            for attr in settings:
                setattr(self, attr, settings[attr])
                
    def __init__(self, screen_rect, difficulty, mode):
        self.default_settings()
        self.set_settings({'difficulty': difficulty, 'mode': mode})
        
        self.screen_rect = screen_rect
        self.star_field = StarField(screen_rect.width, screen_rect.height, 10)
        
        self.dynamics = physics.Dynamics()
        
        self.entity_list = []
        
        self.start_game()
        
        self.add_entity(entity.ShieldPowerup(Vector2D(250, 410), Vector2D(0,0), 0.0, 0.0))
        self.add_entity(entity.WeaponPowerup(Vector2D(300, 410), Vector2D(0,0), 0.0, 0.0))
    
    def default_settings(self):
        self.settings = Game.Settings({'difficulty': GAME_DIFF_MEDIUM, 'mode': GAME_MODE_NORMAL})
        
    def set_settings(self, settings):
        '''
        Sets all the settings.
        '''
        if self.settings != None:
            self.settings.add(settings)
        else:
            self.settings = Game.Settings(settings)
            
        diff = self.settings.difficulty
        if diff == GAME_DIFF_EASY:
            self.settings.add(GAME_SETTINGS_EASY)
        elif diff == GAME_DIFF_MEDIUM:
            self.settings.add(GAME_SETTINGS_MEDIUM)
        elif diff == GAME_DIFF_HARD:
            self.settings.add(GAME_SETTINGS_HARD)
            
    def start_game(self):
        self.create_player()
        self.spawn_player()
        
        self.distance_travelled = 0
        self.distance = self.settings.distance
        self.spawn_timer = 1.0
        self.points = 0
        
        self.game_over = False
        
    def random_vertical_position(self):
        return random.random() * self.screen_rect.height
    
    def probability_event(self, probability):
        rand = random.random()
        if rand <= probability:
            return True
        
        return False
    
    def random_float(self, min, max):
        return min + random.random()*(max-min)
    
    def spawn_asteroid(self):
        position_x = self.screen_rect.width + 100
        position_y = self.random_vertical_position()
        position = Vector2D(position_x, position_y)
        
        v_min = entity.ASTEROID_VELOCITY_MIN
        v_max = entity.ASTEROID_VELOCITY_MAX
        
        speed = self.random_float(v_min, v_max)
        
        velocity = Vector2D(-1.0, 0.0).rotate(self.random_float(-entity.ASTEROID_DIRECTION_SPREAD, entity.ASTEROID_DIRECTION_SPREAD)).scale(speed)
        
        ent = entity.Asteroid(30, position, velocity, 0.0, 0.0)
        self.add_entity(ent)
        
    def spawn_hole(self):
        pass
    def spawn_shield(self):
        pass
    def spawn_weapon(self):
        pass
    
    def update_spawner(self, dt):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0.0:
            self.spawn_timer += GAME_SPAWN_PERIOD
            
            settings = self.settings
            
            spawn_asteroid = self.probability_event(settings.aster_prob)
            spawn_hole = self.probability_event(settings.hole_prob)
            spawn_shield = self.probability_event(settings.shield_prob)
            spawn_weapon = self.probability_event(settings.weapon_prob)
            
            if spawn_asteroid == True:
                # spawn an asteroid
                self.spawn_asteroid()
            if spawn_hole == True:
                # spawn a black hole
                self.spawn_hole()
            if spawn_shield == True:
                # spawn a shield powerup
                self.spawn_shield()
            if spawn_weapon == True:
                # spawn a weapon powerup
                self.spawn_weapon()
                
    def update_distance(self, dt):
        self.distance += GAME_TRAVEL_VELOCITY*dt
            
    def create_player(self):
        self.player = entity.Player(self.settings.default_hp, self.settings.default_regens, Vector2D(self.screen_rect.width/4, self.screen_rect.height/2), Vector2D(0,0), 0.0)
        
    def spawn_player(self):
        self.player.respawn(self.settings.default_hp, Vector2D(self.screen_rect.width/4, self.screen_rect.height/2), Vector2D(0,0), 0.0)
        self.add_entity(self.player)
        
    def wrap_player(self, entity):
        '''
        Keep player on the screen; this
        simplifies things greatly.
        '''
        position = entity.get_position()
        if position.get_x() < 0:
            position.set_x(self.screen_rect.width)
        elif position.get_x() > self.screen_rect.width:
            position.set_x(0)
        if position.get_y() < 0:
            position.set_y(self.screen_rect.height)
        elif position.get_y() > self.screen_rect.height:
            position.set_y(0)
        entity.set_position(position)
        
    def player_destroyed(self):
        self.player.lose_regen()
        self.show_player_explosion()
        if self.player.get_regens_left() <= 0:
            self.game_is_over()
  
            
    def show_player_explosion(self):
        player = self.player
        self.player_explosion = self.show_explosion(player.get_position(), player.get_velocity(), player.get_orientation(), player.get_ang_velocity())
        
    def is_player_finished_exploding(self):
        return False

    def show_explosion(self, position, velocity, orientation, ang_velocity):
        expl = entity.Explosion(position, velocity, orientation, ang_velocity)
        self.add_entity(expl)
        return expl
    
    def add_entity(self, entity):
        if entity != None:
            self.entity_list.append(entity)
    
    def key_down(self, key):
        if key == pygame.K_w or key == pygame.K_UP:
            self.player.accelerate(True)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.player.turn_clockwise()
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.player.turn_counterclockwise()
        elif key == pygame.K_SPACE:
            self.add_entity(self.player.shoot())
    
    def key_up(self, key):
        if key == pygame.K_w or key == pygame.K_UP:
            self.player.accelerate(False)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.player.turn_stop()
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.player.turn_stop()
            
    def remove_offscreen_shot(self, entity):
        if self.screen_rect.colliderect(entity.get_bounding_rect()) == False:
            self.entity_list.remove(entity)
            print "bam"

    # http://en.wikipedia.org/wiki/Newton's_law_of_universal_gravitation
    def hole_gravity_force(self, hole, entity):
        if entity.get_collidable() == False:
            return

        # this G is made up because the real value is much too small for this purpose
        G = 6.67
        disp = hole.get_position().addition(entity.get_position().reversed())
        r_squared = disp.norm_squared()
        r_hat = disp.scaled(1/math.sqrt(r_squared))
        
        force = r_hat.scaled(G * hole.get_mass() * entity.get_mass() / r_squared)
        
        entity.apply_force(force)
        hole.apply_force(force.reversed())
        
    def game_is_over(self):
        '''
        Show game over text, wait a bit, proceed to either high-scores
        or title screen depending on game mode.
        '''
        pass

    def update(self, frametime):
        self.star_field.update(frametime)
        
        self.dynamics.resolve_collisions(self.entity_list, frametime)
        for entity1 in self.entity_list:
            entity1.update(frametime)
            
            # remove Entitys that are destroyed
            if entity1.get_alive() == False:
                if isinstance(entity1, entity.Player):
                    self.player_destroyed()
                self.entity_list.remove(entity1)
                continue
            
            # do Entity type-specific updates
            if isinstance(entity1, entity.Player):
                self.wrap_player(entity1)
            elif isinstance(entity1, entity.Player.Shot):
                self.remove_offscreen_shot(entity1)
            elif isinstance(entity1, entity.Hole):
                # every entity1 is attracted to the hole
                for entity2 in self.entity_list:
                    if entity2 == entity1:
                        continue # avoid divn by zero in hole_gravity_force (zero separation between ent and itself)
                    self.hole_gravity_force(entity1, entity2)
                    
        '''
        Do the spawning and distance updates
        '''
        if self.player.get_alive() == True:
            # spawn Asteroids, Holes and Powerups
            # when the player is alive
            self.update_spawner(frametime)
            self.update_distance(frametime)
        else:
            # spawn the player when they finish exploding
            if self.is_player_finished_exploding():
                self.spawn_player()

                
    def draw(self, surface):
        '''
        Draw the star field and all the
        entities on top, basically.

        '''
        surface.fill((0,0,0))
        self.star_field.draw(surface)
        for entity in self.entity_list:
            entity.draw(surface)
        