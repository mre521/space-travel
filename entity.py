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
        self.frame_time = 1.0
        self.frametimer = self.frame_time
        self.animate = False
        self.anim_num_loops = 0
        self.anim_loop_num = 0
        
    def add_frame(self, image, colorkey):
        img = image.convert()
        img.set_colorkey(colorkey)
        self.frames.append(img)
        
    def get_cur_frame(self):
        return self.curframe
    
    def set_cur_frame(self, curframe):
        self.curframe = curframe
    
    def get_cur_frame_image(self):
        return self.frames[self.curframe]
    
    def set_frame_time(self, frame_time):
        self.frame_time = frame_time
        if self.frametimer > frame_time:
            self.frametimer = frame_time
            
    def go_next_frame(self):
        self.curframe += 1
        if self.curframe == len(self.frames):
            if self.anim_loop_num < self.anim_num_loops:
                self.anim_loop_num += 1
                self.curframe = 0
            else:
                self.animate = False

            
    def set_animate(self, animate):
        self.animate = animate
        if self.animate == True:
            self.loop_num = 0
            
    def set_animation_loops(self, loops):
        self.anim_num_loops = loops
            
    def get_is_animating(self):
        return self.animate
            
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
    
    def apply_damage(self, damage, source):
        self.hp -= damage
        self.set_alive(self.hp > 0)
        
    def update(self, dt):
        Object2D.update(self, dt)
        
        if self.animate == True:
            self.frametimer -= dt
            if self.frametimer <= 0.0:
                self.go_next_frame()
                self.frametimer += self.frame_time
        
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
PLAYER_THRUST = 30000.0
PLAYER_TURN_SPEED = 2*math.pi # half a rotation per second
PLAYER_SHOT_SPEED = 1000.0
PLAYER_SHOT_DAMAGE = 10
PLAYER_SHOT_TIME = 0.5
PLAYER_SHIELD_TIME = 20.0
pygame.mixer.init()
SHOT_SOUND = pygame.mixer.Sound("snd/shot.wav")
SHOT_SOUND.set_volume(0.20)
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
        def __init__(self, parent, damage, position, velocity, orientation):
            
            geometry = (Vector2D(-10,-5), Vector2D(10, -5), Vector2D(10, 5), Vector2D(-10, 5))
            
            Entity.__init__(self, 1, geometry, position, velocity, orientation, 0.0, 100.0)
            
            self.add_frame(pygame.image.load("obj/shot.png"), (255,0,255))
            
            self.damage = damage
            self.parent = parent
            
            SHOT_SOUND.play()
            
        def get_damage(self):
            return self.damage
        
        def get_parent(self):
            return self.parent
        
        def hit_by_entity(self, entity):
            '''
            Shots damage Asteroids and collide
            '''
            if isinstance(entity, Asteroid):
                entity.apply_damage(self.get_damage(), self)
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
        
        self.add_frame(pygame.image.load("obj/ship.png"), (255,0,255))
        
        self.regens_left = regens
        self.invuln_time = 0.0
        self.invuln_flash_time = 0.0
        
        self.points = 0
        
        self.shot_time = PLAYER_SHOT_TIME
        self.shot_damage = PLAYER_SHOT_DAMAGE
        self.shot_speed = PLAYER_SHOT_SPEED

        self.shot_timer = 0.0
        
        self.shield_time = PLAYER_SHIELD_TIME
        self.shield_timer = 0.0
        
        self.turn_speed = math.pi
        self.turn_cw = False
        self.turn_ccw = False
        self.thrust = PLAYER_THRUST
        
        
        self.visible = True
        
        self.accelerate(False)
        
    def respawn(self, hp, position, velocity, orientation):
        self.alive = True
        self.hp = hp
        self.set_position(position)
        self.set_velocity(velocity)
        self.set_velocity(velocity)
        self.make_invuln()
        
        self.shot_timer = 0.0
        
        # remove powerups
        self.shot_time = PLAYER_SHOT_TIME
        self.weapon_upgrades = 0
        self.shield_timer = 0.0
        
    def add_points(self, points):
        self.points += points
        
    def get_points(self):
        return self.points
        
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
        direction = Vector2D(1, 0).rotate(self.orientation)
        shot_velocity = direction.scaled(self.shot_speed)
        shot_velocity.add(self.velocity)
        
        shot_position = self.position.copy().add(direction.scaled(30))
        shot_orientation = self.orientation
        
        return Player.Shot(self, self.shot_damage, shot_position, shot_velocity, shot_orientation)
    
    def can_shoot(self):
        return self.shot_timer <= 0.0
    
    def shoot(self):
        if self.can_shoot() == True:
            self.shot_timer = self.shot_time
            return self.create_shot()
        else:
            return None
        
    def increase_shot_frequency(self):
        self.shot_time *= 0.75
        self.weapon_upgrades += 1
        
    def has_weapon_upgrade(self):
        return self.weapon_upgrades > 0
    
    def get_weapon_upgrades(self):
        return self.weapon_upgrades
        
    def update_shot_timer(self, dt):
        if self.can_shoot() == False:
            self.shot_timer -= dt
            if self.shot_timer < 0.0:
                self.shot_timer = 0.0
                
    def give_shield(self):
        self.shield_timer += self.shield_time
        
    def has_shield(self):
        return self.shield_timer > 0
    
    def get_shield_timer(self):
        return self.shield_timer
    
    def update_shield_timer(self, dt):
        if self.has_shield() == True:
            self.shield_timer -= dt
            if self.shield_timer < 0.0:
                self.shield_timer = 0.0
                
    def turn_clockwise(self):
        self.turn_cw = True
        self.ang_velocity = self.turn_speed
    
    def turn_counterclockwise(self):
        self.turn_ccw = True
        self.ang_velocity = -self.turn_speed
                
    def turn_cw_stop(self):
        self.ang_velocity = 0.0
        self.turn_cw = False
        if self.turn_ccw == True:
            self.turn_counterclockwise()
        
    def turn_ccw_stop(self):
        self.ang_velocity = 0.0
        self.turn_ccw = False
        if self.turn_cw == True:
            self.turn_clockwise()
        
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
        self.update_shield_timer(dt)
        
    def apply_damage(self, damage, source):
        '''
        Overrided to implement Asteroid shield
        '''
        if isinstance(source, Asteroid):
            if self.has_shield() == True:
                return
        else:
            Entity.apply_damage(self, damage, source)
        
    def hit_by_entity(self, entity):
        '''
        Player is damaged by Asteroids,
        Asteroid is destroyed by players
        '''
        if isinstance(entity, Asteroid) == True:
            self.apply_damage(entity.get_damage(), entity)
            entity.set_alive(False)
            return True
        
        '''
        Player is destroyed by Holes
        '''
        if isinstance(entity, Hole) == True:
            self.set_alive(False)
            return False
        
        '''
        Player gains powerups
        '''
        if isinstance(entity, Powerup) == True:
            self.add_points(POWERUP_POINTS)
            entity.give_to(self)
            entity.set_alive(False)
            return False
        
    def draw(self, surface):
        if self.visible == True:
            Entity.draw(self, surface)

    
ASTEROID_DAMAGE = 20
ASTEROID_VELOCITY_MIN = 100
ASTEROID_VELOCITY_MAX = 150
ASTEROID_DIRECTION_SPREAD = math.pi/12 
ASTEROID_POINTS = 100
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
        
        self.add_frame(pygame.image.load("obj/aster.png"), (255,0,255))
        
    def get_damage(self):
        return ASTEROID_DAMAGE
    
    def apply_damage(self, damage, source):
        '''
        Detect asteroid destruction by player
        to assign points
        '''
        was_alive = self.get_alive()
        Entity.apply_damage(self, damage, source)
        
        if isinstance(source, Player.Shot):
            if was_alive != self.get_alive(): # died after applying damage
                source.get_parent().add_points(ASTEROID_POINTS)
            
    def hit_by_entity(self, entity):
        '''
        Players are damaged by Asteroids but the 
        Asteroid is destroyed
        '''
        if isinstance(entity, Player):
            entity.apply_damage(self.get_damage(), self)
            self.set_alive(False)
            return True
        
        '''
        Asteroids are destroyed by Holes
        '''
        if isinstance(entity, Hole):
            self.set_alive(False)
            return False
        
        '''
        Asteroids are damaged by Shots from the 
        Player.
        '''
        if isinstance(entity, Player.Shot):
            self.apply_damage(entity.get_damage(), entity)
            entity.set_alive(False)
            return True
        
        '''
        Asteroids simply bounce off other
        Asteroids.
        '''
        if isinstance(entity, Asteroid):
            return True
        
        
HOLE_VELOCITY_MIN = 80
HOLE_VELOCITY_MAX = 100
HOLE_DIRECTION_SPREAD = math.pi/6 
HOLE_INCOMING = pygame.mixer.Sound("snd/hole_incoming.wav")
HOLE_INCOMING.set_volume(0.5)
class Hole(Entity):
    '''
    Really avoid these.
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
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
        Entity.__init__(self, 1, tuple(geometry), position, velocity, orientation, ang_velocity, mass)
        
        self.add_frame(pygame.image.load("obj/hole.png"), (255,0,255))
        
        # warn player about black hole
        HOLE_INCOMING.play()
        
    def hit_by_entity(self, entity):
        '''
        Holes kill any entity, including other
        Holes, and are not affected by collisions
        '''
        entity.set_alive(False)
        return False
    
POWERUP_VELOCITY_MIN = 200
POWERUP_VELOCITY_MAX = 300
POWERUP_POINTS = 250
POWERUP_SOUND = pygame.mixer.Sound("snd/powerup.wav")
class Powerup(Entity):
    '''
    Something beneficial to the Player
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):

        geometry = (Vector2D(-15, -15), Vector2D(15, -15), 
                    Vector2D(15, 15), Vector2D(-15, 15))
        
        mass = 1.0
        Entity.__init__(self, 1.0, geometry, position, velocity, orientation, ang_velocity, mass)
        
    def give_to(self, player):
        '''
        Specific powerups override to
        implement their specific effect
        '''
        POWERUP_SOUND.play()
 
    
    def hit_by_entity(self, entity):
        '''
        Only affects a Player entity
        '''
        if isinstance(entity, Player):
            self.give_to(entity)
            self.set_alive(False)
            
        if isinstance(entity, Hole):
            self.set_alive(False)
            
        # does not interact physically
        return False
        
class ShieldPowerup(Powerup):
    '''
    Player is not damaged by Asteroids
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
        Powerup.__init__(self, position, velocity, orientation, ang_velocity)
        self.add_frame(pygame.image.load("obj/shield.png"), (255,0,255))
        
    def give_to(self, player):
        Powerup.give_to(self, player)
        player.give_shield()
        
class WeaponPowerup(Powerup):
    '''
    Player gets a better weapon
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
        Powerup.__init__(self, position, velocity, orientation, ang_velocity)
        self.add_frame(pygame.image.load("obj/weapon.png"), (255,0,255))
        
    def give_to(self, player):
        Powerup.give_to(self, player)
        player.increase_shot_frequency()
    
EXPLOSION_SOUND = pygame.mixer.Sound("snd/explosion.wav")
EXPLOSION_SOUND.set_volume(0.50)
class Explosion(Entity):
    '''
    Boom
    '''
    def __init__(self, position, velocity, orientation, ang_velocity):
        geometry = (Vector2D(0,0), Vector2D(20, 20), Vector2D(20, -20))
        Entity.__init__(self, 0, geometry, position, velocity, orientation, ang_velocity, 1.0)
        
        self.add_frame(pygame.image.load("obj/expl1.png"), (255,0,255))
        self.add_frame(pygame.image.load("obj/expl2.png"), (255,0,255))
        self.add_frame(pygame.image.load("obj/expl3.png"), (255,0,255))
        self.add_frame(pygame.image.load("obj/expl4.png"), (255,0,255))
        self.add_frame(pygame.image.load("obj/expl5.png"), (255,0,255))
        self.set_frame_time(1.0/15.0)
        self.set_animation_loops(0)
        self.set_animate(True)
        
        self.set_collidable(False)
        
        EXPLOSION_SOUND.play()
        
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
        return self.get_is_animating() == False
