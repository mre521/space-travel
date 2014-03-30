#
# entity.py - game entities
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

from physics import Object2D
from vector import Vector2D

import pygame

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
        
        # images to be displayed as the Entity
        self.frames = []
        self.curframe = 0
        
        
    def get_cur_frame(self):
        return self.curframe
    
    def get_cur_frame_image(self):
        return self.frames[self.curframe]
    
    def rotate_image(self, surface, radians):
        #center = surface.center
        new = pygame.transform.rotate(surface, 180 * -radians / math.pi)
        return new
    
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
        if len(self.frames) > 0:
            image = self.rotate_image(self.get_cur_frame_image(), self.get_orientation())
            center = image.get_rect().center
            pos =self.get_position().get_int()
            x = pos[0]-center[0]
            y = pos[1]-center[1]
            surface.blit(image, (x,y))
        
        #self.draw_phys(surface)
        
    def hit_by(self, obj, collision):
        do_collision = True
        if isinstance(obj, Entity):
            do_collision = self.hit_by_entity(obj)
            
        if do_collision == True:
            Object2D.hit_by(self, obj, collision)
            
    def hit_by_entity(self, entity):
        '''
        Return True to indicate that 
        collision should be resolved
        '''
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
            
            img = pygame.image.load("obj/shot.png").convert()
            img.set_colorkey((255,0,255))
            self.frames.append(img)
            
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
            
        def draw(self, surface):
            Entity.draw(self, surface)
            #Object2D.draw_phys(self, surface)
        
    def __init__(self, hp, regens, position, velocity, orientation):
        geometry = (Vector2D(-20, 20), Vector2D(10, 15),
                    Vector2D(30, 0),
                    Vector2D(10, -15), Vector2D(-20, -20))
        
        '''geometry = (Vector2D(-20, -20), Vector2D(10, -15),
                    Vector2D(30, 0),
                    Vector2D(10, 15), Vector2D(-20, 20))'''
        
        Entity.__init__(self, hp, geometry, position, velocity, orientation, 0.0, 1.0)
        
        img = pygame.image.load("obj/ship.png").convert()
        img.set_colorkey((255,0,255))
        self.frames.append(img)
        
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
            Entity.draw(self, surface)
            #Object2D.draw_phys(self, surface)
            
        
    #def draw(self, surface):
    #    self.draw_phys(surface)
    
ASTEROID_DAMAGE = 20
class Asteroid(Entity):
    '''
    Avoid these
    '''
    def __init__(self, hp, position, velocity, orientation, ang_velocity):
        
        geometry = (Vector2D(-43, 0), Vector2D(-29, 21), 
                    Vector2D(0, 30), Vector2D(20, 28), 
                    Vector2D(40, 0), Vector2D(30, -28), 
                    Vector2D(0, -37), Vector2D(-29, -22))
        
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
        
    def draw(self, surface):
        Entity.draw(self, surface)
        Object2D.draw_phys(self, surface)
        
class Hole(Entity):
    '''
    Really avoid these.
    '''
    def __init__(self, hp, position, velocity, orientation, ang_velocity):
        '''
        Generates roughly circular
        geometry.
        '''
        geometry = [] # don't remove or exceptions will be raised
        npoints = 8
        arc = -2*math.pi/(npoints)
        radius = 20
        i = 0
        while i < npoints:
            x = radius * math.cos(arc*i)
            y = radius * math.sin(arc*i)
            geometry.append(Vector2D(x, y))
            i+=1
        
        # supermassive - important for the 'gravitational' force
        mass = 50000000.0
        Entity.__init__(self, hp, tuple(geometry), position, velocity, orientation, ang_velocity, mass)
        
    def hit_by_entity(self, entity):
        '''
        Holes kill any entity and are not
        affected by a collision
        '''
        entity.set_alive(False)
        return False
    
class Explosion(Entity):
    '''
    The result of not avoiding Asteroids and Holes
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
        geometry = (Vector2D(0,0), Vector2D(20, 20), Vector2D(20, -20))
        Entity.__init__(self, 0, geometry, position, velocity, orientation, ang_velocity, 1.0)
        
        self.set_collidable(False)
        
    def update(self, dt):
        '''
        Fall through to the default Entity updater
        '''
        Entity.update(self, dt)
        # update frames
        
        # have the game get rid of this Explosion when it's finished
        if self.finished():
            self.set_alive(False)

    
    def finished(self):
        # whether this explosion has finished
        pass
    
    
    def draw(self, surface):
        Object2D.draw_phys(self, surface)
