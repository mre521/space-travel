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

import entity
import physics
import screen

    
STAR_VELOCITY_MEAN = -2000
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
        
        self.star_velocity = STAR_VELOCITY_MEAN
        
        
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
        '''
        Put the star anywhere randomly
        horizontally on the screen.
        Uniformly distributed (presumably)
        '''
        horiz = random.random()*self.width
    
        star.set_position_horiz(horiz)
        
    def random_color(self, star):
        '''
        Because not all stars appear white
        '''
        color = lambda: int(127 + random.random()*128)
        r = color()
        g = color()
        b = color()
        
        star.set_color((r,g,b))
        
    def wrap_star(self, star):
        '''
        Keep re-using the Stars we
        have.
        '''
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
            
# because
pygame.font.init()
            
INFO_DISTANCE_TEXT = "Distance Travelled: "
INFO_POINTS_TEXT = "Points: "
INFO_REGENS_TEXT = "Regens Left: "
INFO_SHIELD_TEXT = "Shield Time Left: "
INFO_WEAPON_TEXT = "Weapon Upgraded: "
INFODISPLAY_FONT = pygame.font.Font("fonts/NEW ACADEMY.ttf", 20)
INFO_TEXT_COLOR = (255,255,255)
class InfoDisplay(object):
    '''
    Displays game information on the screen
    as the game plays out.
    '''
    class Text(object):
        '''
        Helper for InfoDisplay
        '''
        def __init__(self, static_text, initial_value, visible=True):
            self.static = self.create_static(static_text)
            self.value = initial_value
            self.value_text = self.create_static(str(initial_value))
            self.visible = visible
            
        def set_visible(self, visible):
            self.visible = visible
        
        def get_visible(self):
            return self.visible
        
        def create_static(self, text):
            return screen.RenderedText(INFODISPLAY_FONT, text, INFO_TEXT_COLOR, False, True)
        
        def set_value(self, value):
            self.value = value
            self.value_text.set_text(str(value))
            
        def set_position(self, position):
            self.static.set_position(position)
            self.value_text.set_position((position[0]+self.static.get_width(),position[1]))
        
        def get_height(self):
            return self.static.get_height()
        
        def get_with(self):
            return self.static.get_width() + self.value_text.get_width()
            
        def draw(self, surface):
            self.static.draw(surface)
            self.value_text.draw(surface)
            
    def __init__(self, position):
        self.text_list = []
        self.set_position(position)
        
    def add_text(self, info_text):
        self.text_list.append(info_text)
        self.update_text_positions()
        
    def set_position(self, position):
        self.position = position
        self.update_text_positions()
        
    def update_text_positions(self):
        pos_x = self.position[0]
        pos_y = self.position[1]
        for text in self.text_list:
            if text.get_visible() == True:
                text.set_position((pos_x,pos_y))
                pos_y += text.get_height()
        
    def draw(self, surface):
        for text in self.text_list:
            if text.get_visible() == True:
                text.draw(surface)
        
    
HP_TEXT = "HP:"
class HPBar(object):
    '''
    Don't want cluttered code
    so make classes
    '''
    def __init__(self, max_hp, width, height):
        self.set_width(width)
        self.set_height(height)
        
        self.hp_value = 0
        self.hp_max = float(max_hp)
        pass
    
    def set_position(self, position):
        '''
        set position as x,y coordinate tuple
        '''
        self.position = position
        self.hp_static.set_position(position)
        
    def set_width(self, width):
        self.width = width
        
    def set_height(self, height):
        self.height = height
        self.font = pygame.font.Font("fonts/NEW ACADEMY.ttf", height)
        self.hp_static = screen.RenderedText(self.font, HP_TEXT, (0,255,0), False, False, True, False, False, True)
        
    def set_value(self, value):
        self.hp_value = value
        
    def draw(self, surface):
        '''
        Draw a nice HP bar
        '''
        ratio = self.hp_value / self.hp_max
        width_hp = int(self.width * ratio)
        
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.position, (width_hp, self.height)))
        pygame.draw.rect(surface, (127, 127, 127), pygame.Rect(self.position, (self.width, self.height)), 2)
        
        self.hp_static.draw(surface)
        
# three difficulty modes        
GAME_DIFF_EASY = 1
GAME_DIFF_MEDIUM = 2
GAME_DIFF_HARD = 3
# corresponding game settings
GAME_SETTINGS_EASY = {'distance': 1200, 'default_regens': 5, 'default_hp': 100, 'aster_prob': 1.0/5, 'hole_prob': 1.0/35, 'shield_prob': 1.0/10, 'weapon_prob': 1.0/20}
GAME_SETTINGS_MEDIUM = {'distance': 2400, 'default_regens': 4, 'default_hp': 100, 'aster_prob': 1.0/4, 'hole_prob': 1.0/25, 'shield_prob': 1.0/15, 'weapon_prob': 1.0/25}
GAME_SETTINGS_HARD = {'distance': 4800, 'default_regens': 3, 'default_hp': 100, 'aster_prob': 1.0/3, 'hole_prob': 1.0/10, 'shield_prob': 1.0/20, 'weapon_prob': 1.0/30 }
# game modes
GAME_MODE_NORMAL = 1 # fly until destination reached
GAME_MODE_ENDURANCE = 2 # fly until no regenerations left

GAME_TRAVEL_VELOCITY = 10.0 # 10 units of distance per second
GAME_SPAWN_PERIOD = 1.0 # how many seconds between spawning objects

GAME_SHOW_HISCORES = 26 # event injected to show hiscores
GAME_SHOW_TITLE = 27 # event to show titlescreen
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
        self.infodisplay = InfoDisplay((20,20))
        self.populate_info_display()
        
        hp_width = 200
        hp_height = 40
        self.hp_bar = HPBar(self.settings.default_hp, hp_width, hp_height)
        self.hp_bar.set_position((hp_height*2, self.screen_rect.height-hp_height*2))
        
        self.entity_list = []
        
        # Useful to remove entities that fly off the screen too far
        self.despawn_rect = pygame.Rect(self.screen_rect)
        self.despawn_rect.width = self.screen_rect.width + 300
        self.despawn_rect.height = self.screen_rect.height + 100
        self.despawn_rect.center = self.screen_rect.center
        
        self.start_game()

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
        else:
            self.settings.add(GAME_SETTINGS_EASY)
            
    def populate_info_display(self):
        self.distance_text = InfoDisplay.Text(INFO_DISTANCE_TEXT, 0, True)
        self.add_info_text(self.distance_text)
        
        self.points_text = InfoDisplay.Text(INFO_POINTS_TEXT, 0, True)
        self.add_info_text(self.points_text)
        
        self.regens_text = InfoDisplay.Text(INFO_REGENS_TEXT, 0, True)
        self.add_info_text(self.regens_text)
        
        self.shield_text = InfoDisplay.Text(INFO_SHIELD_TEXT, 0.0, False)
        self.add_info_text(self.shield_text)
        
        self.weapon_text = InfoDisplay.Text(INFO_WEAPON_TEXT, 0.0, False)
        self.add_info_text(self.weapon_text)
        
    def add_info_text(self, text):
        self.infodisplay.add_text(text)
        
    def update_distance_display(self):
        value = "%.2f" % self.distance_travelled
        
        if self.settings.mode == GAME_MODE_NORMAL:
            value += " of " + ("%.0f"%self.distance)
        
        self.distance_text.set_value(value)
        
    def update_points_display(self):
        self.points_text.set_value(self.player.get_points())
        
    def update_regens_display(self):
        self.regens_text.set_value(self.player.get_regens_left())
        
    def update_shield_display(self):
        if self.player.has_shield() == True:
            self.shield_text.set_value(("%.2f"%self.player.get_shield_timer()) + " seconds")
            self.shield_text.set_visible(True)
        else:
            self.shield_text.set_visible(False)
            
        self.infodisplay.update_text_positions()
        
    def update_weapon_display(self):
        if self.player.has_weapon_upgrade() == True:
            self.weapon_text.set_value(str(self.player.get_weapon_upgrades()) + " times")
            self.weapon_text.set_visible(True)
        else:
            self.weapon_text.set_visible(False)
            
        self.infodisplay.update_text_positions()
        
    def start_game(self):
        self.create_player()
        self.spawn_player()
        
        self.distance_travelled = 0
        self.distance = self.settings.distance
        self.spawn_timer = 1.0
        self.points = 0
        
        self.update_distance_display()
        self.update_points_display()
        self.update_regens_display()
        self.update_shield_display()
        self.update_weapon_display()
        
        self.shooting = False
        
        self.game_won = False
        self.game_over = False
        
        
    def random_vertical_position(self):
        return random.random() * self.screen_rect.height
    
    def random_position(self):
        position_x = self.screen_rect.width + 100
        position_y = self.random_vertical_position()
        position = Vector2D(position_x, position_y)
        return position
    
    def probability_event(self, probability):
        rand = random.random()
        if rand <= probability:
            return True
        
        return False
    
    def random_float(self, min_, max_):
        return min_ + random.random()*(max_-min_)
    
    def spawn_asteroid(self):
        position = self.random_position()
        
        v_min = entity.ASTEROID_VELOCITY_MIN
        v_max = entity.ASTEROID_VELOCITY_MAX
        
        speed = self.random_float(v_min, v_max)
        
        velocity = Vector2D(-1.0, 0.0).rotate(self.random_float(-entity.ASTEROID_DIRECTION_SPREAD, entity.ASTEROID_DIRECTION_SPREAD)).scale(speed)
        ang_velocity = self.random_float(-entity.ASTEROID_DIRECTION_SPREAD, entity.ASTEROID_DIRECTION_SPREAD)
        
        ent = entity.Asteroid(30, position, velocity, 0.0, ang_velocity)
        self.add_entity(ent)
        
    def spawn_hole(self):
        position = self.random_position()
        
        v_min = entity.HOLE_VELOCITY_MIN
        v_max = entity.HOLE_VELOCITY_MAX
        
        speed = self.random_float(v_min, v_max)
        
        velocity = Vector2D(-1.0, 0.0).rotate(self.random_float(-entity.HOLE_DIRECTION_SPREAD, entity.HOLE_DIRECTION_SPREAD)).scale(speed)
        ang_velocity = self.random_float(-entity.HOLE_DIRECTION_SPREAD, entity.HOLE_DIRECTION_SPREAD)
        
        ent = entity.Hole(position, velocity, 0.0, ang_velocity)
        # holes should be drawn under other entities:
        self.add_entity_bottom(ent)
    
    def spawn_powerup(self, powerup_class):
        position = self.random_position()
        
        v_min = entity.POWERUP_VELOCITY_MIN
        v_max = entity.POWERUP_VELOCITY_MAX
        
        speed = self.random_float(v_min, v_max)
        
        velocity = Vector2D(-1.0, 0.0).scale(speed)
        
        ent = powerup_class(position, velocity, 0.0, 0.0)
        self.add_entity(ent)
    
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
                self.spawn_powerup(entity.ShieldPowerup)
            if spawn_weapon == True:
                # spawn a weapon powerup
                self.spawn_powerup(entity.WeaponPowerup)
                
    def update_distance(self, dt):
        self.distance_travelled += GAME_TRAVEL_VELOCITY*dt
        self.update_distance_display()
        
        if self.settings.mode == GAME_MODE_NORMAL:
            if self.distance_travelled >= self.distance:
                self.distance_travelled = self.distance
                self.game_is_over()
            
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
        '''
        Do what is required when player
        gets destroyed
        '''
        self.player.lose_regen()
        self.update_regens_display()
        self.show_player_explosion()
        if self.player.get_regens_left() <= 0:
            self.game_is_over()
  
            
    def show_player_explosion(self):
        self.player_explosion = self.show_explosion(self.player)
        
    def is_player_finished_exploding(self):
        return self.player_explosion.finished()

    def show_explosion(self, ent):
        expl = entity.Explosion(ent.get_position(), ent.get_velocity(), ent.get_orientation(), ent.get_ang_velocity())
        self.add_entity(expl)
        return expl
    
    def add_entity(self, entity):
        '''
        inserts a new entity into the game
        '''
        if entity != None:
            self.entity_list.append(entity)
            
    def add_entity_bottom(self, entity):
        '''
        inserts a new entity below all others
        '''
        if entity != None:
            self.entity_list.insert(0, entity)
    
    def key_down(self, key):
        if self.game_over == False:
            if key == pygame.K_w or key == pygame.K_UP:
                self.player.accelerate(True)
            if key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.turn_clockwise()
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.turn_counterclockwise()
            if key == pygame.K_SPACE:
                self.shooting = True
            elif key == pygame.K_k: # kill yourself
                if self.player.get_alive() == True:
                    self.player.set_hp(0)
                    self.player.set_alive(False)
                    self.player_destroyed()
                    self.entity_list.remove(self.player)
            elif key == pygame.K_p: # win the game
                self.distance_travelled = self.distance
        else:
            if key == pygame.K_RETURN:
                if self.settings.mode == GAME_MODE_NORMAL or self.settings.mode == GAME_MODE_ENDURANCE:
                    pygame.event.post(pygame.event.Event(GAME_SHOW_HISCORES))
                else:
                    pygame.event.post(pygame.event.Event(GAME_SHOW_TITLE))
    
    def key_up(self, key):
        if self.game_over == False:
            if key == pygame.K_w or key == pygame.K_UP:
                self.player.accelerate(False)
            if key == pygame.K_RIGHT or key == pygame.K_d:
                self.player.turn_cw_stop()
            if key == pygame.K_LEFT or key == pygame.K_a:
                self.player.turn_ccw_stop()
            if key == pygame.K_SPACE:
                self.shooting = False
                
    def player_fire_weapon(self):
        if self.shooting:
            if self.player.can_shoot():
                self.add_entity(self.player.shoot())
            
    def remove_offscreen_entity(self, entity):
        '''
        Remove entities that have gone too
        far off screen
        -> Reduce lag
        '''
        if self.despawn_rect.colliderect(entity.get_bounding_rect()) == False:
            self.entity_list.remove(entity)
            return True
        else:
            return False

    # http://en.wikipedia.org/wiki/Newton's_law_of_universal_gravitation
    def hole_gravity_force(self, hole, entity):
        if entity.get_collidable() == False:
            return

        # this G is made up because the real value is much too small for this purpose
        G = 6.67 # x 10^-11
        disp = hole.get_position().addition(entity.get_position().reversed())
        r_squared = disp.norm_squared()
        r_hat = disp.scaled(1/math.sqrt(r_squared))
        
        force = r_hat.scaled(G * hole.get_mass() * entity.get_mass() / r_squared)
        
        entity.apply_force(force)
        hole.apply_force(force.reversed())
        
    def game_is_over(self):
        '''
        End the game.
        
        This function could really be
        cleaned up but other things are
        more important at the moment.
        '''
        self.game_over = True
        
        self.final_points = self.player.get_points()
        self.final_distance = self.distance_travelled
        
        game_over_font = pygame.font.Font("fonts/Rase-GPL-Bold.otf", 40)
        message_font = pygame.font.Font("fonts/NEW ACADEMY.ttf", 20)
        self.game_over_text = screen.RenderedText(game_over_font, "Game Over.", (0, 255, 0), True)
        self.game_over_text.set_position(((self.screen_rect.width/2, self.screen_rect.height/3)))
        
        if self.settings.mode == GAME_MODE_NORMAL:
            if self.distance_travelled >= self.distance:
                message1_text = "Winner, you have reached the destination!"
                message2_text = "You collected " + str(self.player.get_points()) + " points along the way."
                message3_text = "Press enter to record your score for everyone to see."
            else:
                message1_text = "What a pity, you didn't make it." 
                message2_text = "You only had a distance of " + ("%.2f"%(self.distance-self.distance_travelled)) + " left too..."
                message3_text = "Press enter key to see everyone else who did better than you."
        elif self.settings.mode == GAME_MODE_ENDURANCE:
            message1_text = "You endured a distance of " + ("%.2f"%(self.distance_travelled)) + ". Congratulations."
            message2_text = "You also collected " + str(self.player.get_points()) + " points along the way."
            message3_text = "Press enter key to record your score."
        else:
            message1_text = "Well this is unusual, I don't know this game mode."
            message2_text = "Press enter key, anyway, to return to the title screen."
            message3_text = ""
            
        x = self.game_over_text.get_x()
        y = self.game_over_text.get_y() + self.game_over_text.get_height()
            
        self.game_over_message1 = screen.RenderedText(message_font, message1_text, (255, 255, 255), True)
        self.game_over_message1.set_position((x,y))
        y += self.game_over_message1.get_height()
        
        self.game_over_message2 = screen.RenderedText(message_font, message2_text, (255, 255, 255), True)
        self.game_over_message2.set_position((x,y))
        y += self.game_over_message2.get_height()
        
        self.game_over_message3 = screen.RenderedText(message_font, message3_text, (255, 255, 255), True)
        self.game_over_message3.set_position((x,y))
        y += self.game_over_message3.get_height()
        
    def get_final_points(self):
        return self.final_points
    
    def get_final_distance(self):
        return self.final_distance
    
    def get_game_mode(self):
        return self.settings.mode
    
    def get_game_difficulty(self):
        return self.settings.difficulty
        
    def game_over_draw(self, surface):
        '''
        Show game over/win text
        '''
        self.game_over_text.draw(surface)
        self.game_over_message1.draw(surface)
        self.game_over_message2.draw(surface)
        self.game_over_message3.draw(surface)

    def update(self, frametime):
        self.star_field.update(frametime)
        
        self.dynamics.resolve_collisions(self.entity_list, frametime)
        for entity1 in self.entity_list:
            entity1.update(frametime)
            
            # remove Entitys that are destroyed;
            # update powerup info if it was a powerup
            if entity1.get_alive() == False:
                if isinstance(entity1, entity.Player):
                    self.player_destroyed()
                elif isinstance(entity1, entity.WeaponPowerup):
                    self.update_weapon_display()
                elif isinstance(entity1, entity.Asteroid):
                    self.show_explosion(entity1)
                self.update_points_display()
                    
                self.entity_list.remove(entity1)
                continue # we don't need to do anything more with a dead Entity
            
            # remove Entitys that are outside of 
            # the allowable region
            if self.remove_offscreen_entity(entity1) == True:
                continue
            
            # do Entity type-specific updates
            if isinstance(entity1, entity.Player):
                self.wrap_player(entity1)
            elif isinstance(entity1, entity.Hole):
                # every entity1 is attracted to the hole
                for entity2 in self.entity_list:
                    if entity2 == entity1:
                        continue # avoid divn by zero in hole_gravity_force (zero separation between ent and itself)
                    self.hole_gravity_force(entity1, entity2)
                    
        # update shield powerup display
        self.update_shield_display()
                    
        # update HP bar, regardless of if dead or not
        self.hp_bar.set_value(self.player.get_hp())
        
        '''
        Do the spawning and distance updates
        '''
        if self.game_over == False:
            if self.player.get_alive() == True:
                # spawn Asteroids, Holes and Powerups
                # when the player is alive
                self.update_spawner(frametime)
                self.update_distance(frametime)
                
                self.player_fire_weapon()
            else:
                # spawn the player when they finish exploding
                if self.is_player_finished_exploding():
                    self.spawn_player()
                    
                
    def draw(self, surface):
        '''
        Draw the star field and all the
        entities on top, basically.
        draw info texts and hp bar as well
        '''
        surface.fill((0,0,0))
        self.star_field.draw(surface)
        for entity in self.entity_list:
            entity.draw(surface)
            
        if self.game_over == False:
            self.hp_bar.draw(surface)
            self.infodisplay.draw(surface)
        else:
            self.game_over_draw(surface)
        
        