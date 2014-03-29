#
# game.py - core game functionality
#
# PygameGame
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
import physics

        
        
class Entity(Object2D):
    '''
    An movable, colidable, displayable object of form in
    the Game.
    '''
    def __init__(self, hp, geometry, position, velocity, orientation, ang_velocity, mass):
        Object2D.__init__(self, position, velocity, orientation, ang_velocity, mass)
        
        self.hp = hp
        self.alive = True
        self.set_geometry(geometry)
    
    def get_hp(self):
        return self.hp
    
    def set_hp(self, hp):
        self.hp = hp
        self.set_alive(self.hp > 0)
        
    def set_alive(self, alive):
        self.alive = alive
        
    def get_alive(self):
        return self.alive
    
    def apply_damage(self, damage):
        self.hp -= damage
        self.set_alive(self.hp > 0)
        
    def update(self, dt):
        Object2D.update(self, dt)
        
    def draw(self, surface):
        self.draw_phys(surface)
        
    def hit_by(self, obj, collision):
        do_collision = True
        if isinstance(obj, Entity):
            do_collision = self.hit_by_entity(obj)
            
        if do_collision == True:
            Object2D.hit_by(self, obj, collision)
            
    def hit_by_entity(self, entity):
        return True
        

        
# number of seconds player is invulnerable after spawning
PLAYER_INVULN_TIME = 3.0
# time in seconds between player visible/nonvisible flash after spawning
PLAYER_INVULN_FLASH_PERIOD = 0.0625
PLAYER_THRUST = 10000.0
PLAYER_TURN_SPEED = math.pi # half a rotation per second
PLAYER_SHOT_SPEED = 1000.0
PLAYER_SHOT_DAMAGE = 10
PLAYER_SHOT_TIME = 0.5
class Player(Entity):
    '''
    The Entity controlled by the player;
    the ship.
    '''
    class Shot(Entity):
        '''
        That which is projected from the weapon
        of the Player.
        '''
        def __init__(self, damage, position, velocity, orientation):
            
            geometry = (Vector2D(-10,-5), Vector2D(10, -5), Vector2D(10, 5), Vector2D(-10, 5))
            
            Entity.__init__(self, 1, geometry, position, velocity, orientation, 0.0, 100.0)
            
            self.damage = damage
            
        def get_damage(self):
            return self.damage
        
        def hit_by_entity(self, entity):
            '''
            Shots damage Asteroids and collide
            '''
            if isinstance(entity, Asteroid):
                entity.apply_damage(self.get_damage())
                self.set_alive(False)
                return True
            
            '''
            Holes consume shots
            '''
            if isinstance(entity, Hole):
                self.set_alive(False)
                return False
        
    def __init__(self, hp, regens, position, velocity, orientation):
        
        geometry = (Vector2D(-20, 20), Vector2D(10, 15),
                    Vector2D(30, 0),
                    Vector2D(10, -15), Vector2D(-20, -20))
        
        '''geometry = (Vector2D(-20, -20), Vector2D(10, -15),
                    Vector2D(30, 0),
                    Vector2D(10, 15), Vector2D(-20, 20))'''
        
        Entity.__init__(self, hp, geometry, position, velocity, orientation, 0.0, 1.0)
        
        self.has_shield = False
        self.shot_time = PLAYER_SHOT_TIME
        self.shot_damage = PLAYER_SHOT_DAMAGE
        self.shot_speed = PLAYER_SHOT_SPEED

        self.shot_timer = 0.0
        
        self.turn_speed = math.pi
        self.thrust = PLAYER_THRUST
        
        self.regens_left = regens
        self.invuln_time = 0.0
        self.invuln_flash_time = 0.0
        
        self.visible = True
        
        self.accelerate(False)
        
    def respawn(self, hp, position, velocity, orientation):
        self.alive = True
        self.hp = hp
        self.set_position(position)
        self.set_velocity(velocity)
        self.set_velocity(velocity)
        self.make_invuln()
        
    def make_invuln(self):
        self.set_collidable(False)
        self.invuln_time = PLAYER_INVULN_TIME
        self.invuln_flash_time = PLAYER_INVULN_FLASH_PERIOD
        
    def is_invuln(self):
        return self.invuln_time > 0.0
    
    def invuln_flash(self, dt):
        self.invuln_flash_time -= dt
        if self.invuln_flash_time <= 0.0:
            self.visible = not self.visible
            self.invuln_flash_time = PLAYER_INVULN_FLASH_PERIOD
            
    def create_shot(self):
        shot_velocity = Vector2D(1, 0).rotate(self.orientation).scale(self.shot_speed)
        shot_velocity.add(self.velocity)
        
        shot_position = self.position.copy()
        shot_orientation = self.orientation
        
        return Player.Shot(self.shot_damage, shot_position, shot_velocity, shot_orientation)
    
    def can_shoot(self):
        return self.shot_timer <= 0.0
    
    def shoot(self):
        if self.can_shoot() == True:
            self.shot_timer = self.shot_time
            return self.create_shot()
        else:
            return None
        
    def update_shot_timer(self, dt):
        if self.can_shoot() == False:
            self.shot_timer -= dt
            if self.shot_timer < 0.0:
                self.shot_timer = 0.0
                
    def turn_clockwise(self):
        self.ang_velocity = self.turn_speed
    
    def turn_counterclockwise(self):
        self.ang_velocity = -self.turn_speed
                
    def turn_stop(self):
        self.ang_velocity = 0.0
        
    def accelerate(self, accel):
        self.accelerating = accel
        
    def lose_regen(self):
        self.regens_left -= 1
        
    def get_regens_left(self):
        return self.regens_left

    def update(self, dt):
        if self.accelerating == True:
            self.apply_oriented_force(self.thrust)
        
        if self.is_invuln() == True:
            self.invuln_time -= dt
            self.invuln_flash(dt)  
            if self.is_invuln() == False:
                self.set_collidable(True)
                self.visible = True
                
        Entity.update(self, dt)
        self.update_shot_timer(dt)
        
    def hit_by_entity(self, entity):
        '''
        Player is damaged by Asteroids,
        Asteroid is destroyed by players
        '''
        if isinstance(entity, Asteroid):
            self.apply_damage(entity.get_damage())
            entity.set_alive(False)
            return True
        
        '''
        Player is destroyed by Holes
        '''
        if isinstance(entity, Hole):
            self.set_alive(False)
            return False
        
    def draw(self, surface):
        if self.visible == True:
            Object2D.draw_phys(self, surface)
            
        
    #def draw(self, surface):
    #    self.draw_phys(surface)
    
ASTEROID_DAMAGE = 20
class Asteroid(Entity):
    '''
    Avoid these
    '''
    def __init__(self, hp, position, velocity, orientation, ang_velocity):
        
        geometry = (Vector2D(-43, 0), Vector2D(-29, 21), Vector2D(0, 30), Vector2D(20, 28), Vector2D(40, 0), Vector2D(30, -28), Vector2D(0, -37), Vector2D(-29, -22))
        
        Entity.__init__(self, hp, geometry, position, velocity, orientation, ang_velocity, 1000.0)
        
    def get_damage(self):
        return ASTEROID_DAMAGE
    
    def hit_by_entity(self, entity):
        '''
        Players are damaged by Asteroids but the 
        Asteroid is destroyed
        '''
        if isinstance(entity, Player):
            entity.apply_damage(self.get_damage())
            self.set_alive(False)
            return True
        
        '''
        Asteroids are destroyed by Holes
        '''
        if isinstance(entity, Hole):
            self.set_alive(False)
            return False
        
        '''
        Asteroids are destroyed if they hit a player
        but they still hurt the player.
        '''
        if isinstance(entity, Player.Shot):
            self.apply_damage(entity.get_damage())
            entity.set_alive(False)
            return True
        
        '''
        Asteroids simply bounce off other
        Asteroids.
        '''
        if isinstance(entity, Asteroid):
            return True
        
class Hole(Entity):
    '''
    Really avoid these.
    '''
    def __init__(self, hp, position, velocity, orientation, ang_velocity):
        
        geometry = []
        
        npoints = 8
        arc = -2*math.pi/(npoints)
        radius = 20
        i = 0
        while i < npoints:
            x = radius * math.cos(arc*i)
            y = radius * math.sin(arc*i)
            geometry.append(Vector2D(x, y))
            i+=1
        
        #geometry = (Vector2D(-20, 0), Vector2D(-, 21), Vector2D(0, 30), Vector2D(20, 28), Vector2D(40, 0), Vector2D(30, -28), Vector2D(0, -37), Vector2D(-29, -22))
        
        # supermassive
        Entity.__init__(self, hp, tuple(geometry), position, velocity, orientation, ang_velocity, 50000000.0)
        
    def hit_by_entity(self, entity):
        '''
        Holes kill any entity and are not affected by a collision
        '''
        entity.set_alive(False)
        return False
    
class Explosion(Entity):
    '''
    The result of not avoiding obstacles
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
        geometry = (Vector2D(0,0))
        Entity.__init__(self, 0, geometry, position, velocity, orientation, ang_velocity)
        
        self.set_collidable(False)
        
    def update(self, dt):
        
        # update frames
        pass
    
    def finished(self):
        # whether this explosion has finished
        pass
    
    
    def draw(self, surface):
        pass
    
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
        
        self.star_velocity = -2000.0
        
        self.stars = []
        i = 0
        while i < self.num_stars:
            star = StarField.Star()
            self.distribute_horiz(star)
            self.distribute_vert(star)
            self.stars.append(star)
            i += 1
    
    def distribute_vert(self, star):
        factor = -2.0
        
        while math.fabs(factor) > 1.0:
            factor = random.gauss(0.0, 0.75)
            
        vertical = (factor * self.height/2) + self.height/2
            
        velocity = (1.0-math.fabs(factor)) * self.star_velocity
        
        star.set_size((1.0-math.fabs(factor)) * 6)
        
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
GAME_SETTINGS_EASY = {'distance': 1000, 'default_regens': 5, 'default_hp': 100, 'aster_freq': 1.0, 'hole_freq': 0.125, 'shield_freq': 0.25, 'weapon_freq': 0.25}
GAME_SETTINGS_MEDIUM = {'distance': 2000, 'default_regens': 3, 'default_hp': 100, 'aster_freq': 3.0, 'hole_freq': 0.25, 'shield_freq': 0.125, 'weapon_freq': 0.125}
GAME_SETTINGS_HARD = {'distance': 5000, 'default_regens': 2, 'default_hp': 100, 'aster_freq': 4.0, 'hole_freq': 0.30, 'shield_freq': 0.10, 'weapon_freq': 0.10 }
GAME_MODE_NORMAL = 1
GAME_MODE_ENDURANCE = 2
class Game(object):
    '''
    The whole reason for creating every other class.
    '''
    class Settings(object):
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
        
        self.create_player()
        self.spawn_player()
        
        self.game_over = False
        self.distance_travelled = 0
        
        self.points = 0
        
        self.add_entity(Asteroid(30, Vector2D(300, 400), Vector2D(0,0), 0.0, 0.0))
        self.add_entity(Hole(30, Vector2D(500, 300), Vector2D(0,0), 0.0, 0.0))
    
    def default_settings(self):
        self.settings = Game.Settings({'difficulty': GAME_DIFF_MEDIUM, 'mode': GAME_MODE_NORMAL})
        
    def set_settings(self, settings):
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
            
    def create_player(self):
        self.player = Player(self.settings.default_hp, self.settings.default_regens, Vector2D(self.screen_rect.width/4, self.screen_rect.height/2), Vector2D(0,0), 0.0)
        self.add_entity(self.player)
        
    def spawn_player(self):
        self.player.respawn(self.settings.default_hp, Vector2D(self.screen_rect.width/4, self.screen_rect.height/2), Vector2D(0,0), 0.0)
        
    def wrap_player(self, entity):
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
        if self.player.get_regens_left() <= 0:
            self.game_is_over()
            self.entity_list.remove(self.player)
        else:
            self.show_player_explosion()
            
    def show_player_explosion(self):
        player = self.player
        self.player_explosion = self.show_explosion(player.get_position(), player.get_velocity(), player.get_orientation(), player.get_ang_velocity())
        

    def show_explosion(self, position, velocity, orientation, ang_velocity):
        expl = Explosion(position, velocity, orientation, ang_velocity)
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
        for entity in self.entity_list:
            entity.update(frametime)
            
            # remove Entitys that are destroyed unless it is the player
            if entity.get_alive() == False:
                if isinstance(entity, Player):
                    self.player_destroyed()
                else:
                    self.entity_list.remove(entity)
                continue
            
            # do Entity type-specific updates
            if isinstance(entity, Player):
                self.wrap_player(entity)
            elif isinstance(entity, Player.Shot):
                self.remove_offscreen_shot(entity)
            elif isinstance(entity, Hole):
                # every entity is attracted to the hole
                for entity2 in self.entity_list:
                    if entity2 == entity:
                        continue # avoid div by zero in hole_gravity_force
                    self.hole_gravity_force(entity, entity2)

                
    def draw(self, surface):
        surface.fill((0,0,0))
        self.star_field.draw(surface)
        for entity in self.entity_list:
            entity.draw(surface)
        