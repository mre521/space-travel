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

import pygame.mixer
import pygame.draw
import pygame.image
import pygame.font

from vector import Vector2D
from physics import Object2D
import physics


BGM_STOPPED = 25
class BGM(object):
    '''
    Encapsulates background music functionality.
    '''
    def __init__(self, filename):
        self.filename = filename
        
    def play(self, volume):
        pygame.mixer.music.load(self.filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_endevent(BGM_STOPPED)
        
    def pause(self):
        pygame.mixer.pause()
        
    def stop(self, time):
        pygame.mixer.music.fadeout(time)
        
    @staticmethod
    def playing():
        return pygame.mixer.music.get_busy()

class BGImage(object):
    '''
    Encapsulates background image functionality.
    '''
    def __init__(self, filename, width, height):
        self.load(filename, width, height)
        
    def load(self, filename, width, height):
        self.filename = filename
        self.dimensions = (width, height)
        
        if filename != None:
            self.image = pygame.image.load(filename).convert()
            self.image_scaled = pygame.transform.smoothscale(self.image, self.dimensions)
        else:
            self.image = None
            self.image_scaled = None
        
    def set_scaled(self, scaled):
        self.scaled = scaled
        
    def get_surface(self):
        if self.scaled == False:
            return self.image
        else:
            return self.image_scaled
        
    def draw(self, dest):
        surface = self.get_surface()
        return dest.blit(surface, (0,0))
        
pygame.font.init()

class RenderedText(object):
    '''
    Holds a piece of rendered text using the given font and options
    '''
    def __init__(self, font, text, color, center_x=False, center_y=False, antialias=True, underline=False, bold=False, italic=False, background=None):
        self.font = font
        self.text = text
        
        font.set_underline(underline)
        font.set_bold(bold)
        font.set_italic(italic)
        
        # required for font.render to function properly when None is
        # given for background
        if background == None:
            self.surface = font.render(text, antialias, color).convert_alpha()
        else:
            self.surface = font.render(text, antialias, color, background).convert()
            
        
        self.set_position((0,0))
        self.set_center_x(center_x)
        self.set_center_y(center_y)
        
        
    def get_width(self):
        return self.surface.get_width()
    
    def get_height(self):
        return self.surface.get_height()
    
    def set_position(self, position):
        self.position = position
        
    def get_position(self):
        return self.position
    
    def get_x(self):
        return self.position[0]
    
    def get_y(self):
        return self.position[1]
        
    def set_center_x(self, center_x):
        self.center_x = center_x
        if center_x == True:
            self.offset_x = self.get_width()/2
        else:
            self.offset_x = 0
        
    def set_center_y(self, center_y):
        self.center_y = center_y
        if center_y == True:
            self.offset_y = self.get_height()/2
        else:
            self.offset_y = 0
        
    def get_real_position(self):
        return (self.position[0]-self.offset_x, self.position[1]-self.offset_y)
    
    def get_Rect(self):
        return pygame.Rect(self.get_real_position(), (self.get_width(), self.get_height()))
    
    def draw(self, surface):
        real_position = self.get_real_position()
        return surface.blit(self.surface, real_position)
    

MENU_TITLE_FONT = pygame.font.Font("fonts/NEW ACADEMY.ttf", 50)
MENU_MEMBER_FONT = pygame.font.Font("fonts/NEW ACADEMY.ttf", 40)
MENU_TITLE_COLOR = (255,255,255)
MENU_MEMBER_COLOR = (255,127,255)
class Menu(object):
    def __init__(self, title, enter_function=None, title_font=MENU_TITLE_FONT, member_font=MENU_MEMBER_FONT):
        self.title = title
        self.enter_function = enter_function
        self.title_font = title_font
        self.member_font = member_font
        
        self.render_title()
        
        self.members = []
        self.members_text = []
        self.selected_index = 0
        
        self.set_position()
        self.set_parent()
        
    def render_title(self):
        self.title_text = RenderedText(self.title_font, self.title,MENU_TITLE_COLOR, True,False,True,False,True,True)
        self.title_text.set_center_x(True)
        self.title_text.set_center_y(False)
        
    def get_title_width(self):
        return self.title_text.get_width()
    
    def get_title_height(self):
        return self.title_text.get_height()
    
    def get_title(self):
        return self.title
        
    def set_position(self, position=(0,0)):
        self.position = position
        cur_x = position[0]
        cur_y = position[1]
        
        self.title_text.set_position(position)
        cur_y += self.title_text.get_height()
        
        for member_text in self.members_text:
            member_text.set_position((cur_x, cur_y))
            cur_y += member_text.get_height()
            
    def add_member(self, member):
        self.members.append(member)
        self.members_text.append(RenderedText(MENU_MEMBER_FONT, member.get_title(), MENU_MEMBER_COLOR, True, False))
        self.set_position(self.position) # update member text positions including the new member
        member.set_parent(self)
            
    def get_member_text(self, index):
        return self.members_text[index]
            
    def wrap_selection(self):
        max_index = len(self.members)-1
        
        while self.selected_index > max_index:
            self.selected_index -= max_index+1
            
        while self.selected_index < 0:
            self.selected_index += max_index+1
            
    def select(self, selection):
        if len(self.members) > 0:
            self.selected_index = selection
            self.wrap_selection()
        
    def select_next(self):
        self.select(self.selected_index + 1)
        
    def select_prev(self):
        self.select(self.selected_index - 1)
        
    def enter(self, enter_parameter):
        '''
        Enters a sub menu (returns the selected member) or calls
        the provided enter function
        '''
        try:
            selected = self.members[self.selected_index]
            if selected.enter_function == None:
                selected.set_position(self.position)
                return selected
            else:
                selected.enter_function(enter_parameter)
        except Exception as e:
            print e
            return None
        
    def exit(self):
        '''
        Exits this menu (returns the nparent menu)
        '''
        return self.parent
        
    def set_parent(self, parent=None):
        '''
        Set this Menu's parent Menu
        '''
        self.parent = parent
        
    def draw_title(self, surface):
        self.title_text.draw(surface)
        
    def draw_members(self, surface):
        index = 0
        for member_text in self.members_text:
            member_text.draw(surface)
            if index == self.selected_index:
                select_rect = member_text.get_Rect()
                pygame.draw.rect(surface, (0,255,0), select_rect, 4)
            index+=1
    
    def draw(self, surface):
        self.draw_title(surface)
        self.draw_members(surface)
        
class Screen(object):
    '''
    Encapulates one screen of the game.
    
    Provides the basic framework for event handling,
    updating, drawing, background music, and background image.
    
    Should be subclassed to create different game screens
    such as title screen or in-game.
    '''

    def __init__(self, width, height, app, display):
        '''
        Creates this Screen with a width and height to be shown
        on display. 
        
        '''
        self.width = width
        self.height = height
        
        self.app_parent = app
        
        self.rect = pygame.Rect(0, 0, width, height)
        
        self.display = display
        
        self.set_bgm(None)
        self.set_bg_image(None)
        self.set_bg_scaled(False)
        self.set_should_draw_bg(False)
        
        self.bgm_wait = False
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_rect(self):
        return self.rect
    
    def get_display(self):
        return self.display
    
    def set_bgm(self, filename):
        if filename != None:
            self.bgm = BGM(filename)
        else:
            self.bgm = None
        
    def set_bgm_volume(self, volume):
        self.bgm_volume = volume
        
    def set_bgm_fadetime(self, time):
        self.bgm_fadetime = time
        
    def start_bgm(self):
        self.bgm.play(self.bgm_volume)
        
    def stop_bgm(self):
        self.bgm.stop(self.bgm_fadetime)
        
    def set_bg_image(self, filename):
        self.bg = BGImage(filename, self.get_width(), self.get_height())
            
    def set_bg_scaled(self, scaled):
        self.bg.set_scaled(scaled)
        
    def get_bg_image(self):
        return self.bg.get_surface()
        
    def set_should_draw_bg(self, draw):
        self.draw_bg = draw
        
    def activate(self):
        '''
        Set up things when this screen is to be shown.
        Examples are things which run in the background
        '''
        if self.bgm != None:
                if BGM.playing() == True:
                    self.bgm_wait = True
                else:
                    self.start_bgm()
                    
    
    def deactivate(self):
        '''
        Stop tasks when this screen is not being viewed.
        Examples include BGM and other background tasks
        '''
        if self.bgm != None:
            self.stop_bgm()
            
    def handle_events(self, events):
        for event in events:
            if event.type == BGM_STOPPED:
                if self.bgm_wait == True:
                    self.start_bgm()
                    self.bgm_wait = False
            else:
                self.handle_event(event)
            
    def handle_event(self, event):
        pass
    
    def update(self, frametime):
        pass
    
    def draw(self):
        if self.draw_bg == True:
            self.bg.draw(self.display)

TEXT_FONT = pygame.font.Font("fonts/NEW ACADEMY.ttf", 16)
class TextScreen(Screen):
    '''
    Shows text over a background either statically
    or in a scrolling fashion.
    '''
    def __init__(self, width, height, app, display):
        Screen.__init__(self, width, height, app, display)
        
        self.title = "Text Screen"
        
        self.set_scroll(False)
        self.set_scroll_rate(0.0)
        
        self.set_text("")
        self.set_text_color((0,0,0))
        
    def set_scroll(self, scroll):
        self.scroll = scroll
        
    def set_scroll_rate(self, scroll_rate):
        '''
        Set text scroll rate in lines per second
        '''
        self.scroll_rate = scroll_rate
        
    def set_text(self, text):
        self.text = text
        if len(text) > 0:
            self.generate_lines()
        
    def set_text_color(self, color):
        self.color = color
        
    def generate_lines(self):
        self.rendered_lines = []
        text_lines = self.text.split('\n')
        for line in text_lines:
            rendered = RenderedText(TEXT_FONT, line, self.color)
            self.rendered_lines.append(rendered)
            
    def set_text_position(self, position):
        pos_x = position[0]
        pos_y = position[1]
        self.position = (float(pos_x), float(pos_y))
        for line in self.rendered_lines:
            line.set_position((int(pos_x), int(pos_y)))
            pos_y += line.get_height()

    def update(self, frametime):
        if len(self.rendered_lines) > 0 and self.scroll == True:
            line_height = self.rendered_lines[0].get_height()
            new_position = (self.position[0], self.position[1] - self.scroll_rate * line_height * frametime)
            self.set_text_position(new_position)
        
            last_line = self.rendered_lines[-1]
            if (last_line.get_y() + last_line.get_height()) < 0:
                self.position = (self.position[0], float(self.height))
    
    def draw(self):
        self.display.fill((0,0,0))
        for line in self.rendered_lines:
            line.draw(self.display)
        pygame.display.flip()
        
    def go_back(self):
        self.app_parent.screen_close()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.go_back()
        

TITLE_FONT = pygame.font.Font("fonts/Rase-GPL-Bold.otf", 40)
class TitleScreen(Screen):
    '''
    Does the game's title screen.
    '''
    def __init__(self, width, height, app, display):
        Screen.__init__(self, width, height, app, display)
        pygame.mixer.init()
        
        self.set_bgm("BGM/SATELL.S3M")
        self.set_bgm_volume(1.0)
        self.set_bgm_fadetime(1000)
        
        self.set_bg_image("BG/Title.jpg")
        self.set_bg_scaled(True)
        self.set_should_draw_bg(True)
        
        self.title_text = RenderedText(TITLE_FONT, "GAME NAME HERE", (0, 255, 0), True, True)
        self.title_text.set_position((self.display.get_width()/2, self.display.get_height()/6))
        
        self.menu = Menu("Main Menu")
        self.menu.set_position((self.display.get_width()/2, self.display.get_height()/3))
        
        start_menu = Menu("Start Game", TitleScreen.start_game)
        #start_menu.add_member(Menu("Easy Difficulty"))
        #start_menu.add_member(Menu("Medium Difficulty"))
        #start_menu.add_member(Menu("Hard Difficulty"))
        
        self.menu.add_member(start_menu)
        self.menu.add_member(Menu("Options"))
        self.menu.add_member(Menu("Story", TitleScreen.show_story))
        self.menu.add_member(Menu("Controls"))
        self.menu.add_member(Menu("Credits", TitleScreen.show_credits))
        self.menu.add_member(Menu("Exit", TitleScreen.quit_game))
        
        self.angle = 0
        self.prevrect = None
        
    def activate(self):
        Screen.activate(self)
        
    def deactivate(self):
        Screen.deactivate(self)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.menu.select_next()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.menu.select_prev()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.menu_enter()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.menu_exit()
                
    def menu_prev(self):
        self.menu.select_prev()
    
    def menu_next(self):
        self.menu.select_next()
        
    def menu_enter(self):
        menu = self.menu.enter(self)
        if type(menu) == type(self.menu):
            self.menu = menu

    def menu_exit(self):
        menu = self.menu.exit()
        if type(menu) == type(self.menu):
            self.menu = menu
            
    def start_game(self):
        gamescreen = InGameScreen(self.width, self.height, self.app_parent, self.display)
        gamescreen.start_game(GAME_DIFF_MEDIUM, GAME_MODE_NORMAL)
        self.app_parent.screen_open(gamescreen)
            
    def show_story(self):
        story = TextScreen(self.width, self.height, self.app_parent, self.display)
        story.set_text_color((255,255,255))
        
        text_file = open("txt/story.txt", "r")
        text = text_file.read()
        text_file.close()
        
        story.set_text(text)
        
        story.set_text_position((self.width/20, self.height/10))
        self.app_parent.screen_open(story)
            
    def show_credits(self):
        credits = TextScreen(self.width, self.height, self.app_parent, self.display)
        credits.set_text_color((255,255,255))
        credits.set_scroll(True)
        credits.set_scroll_rate(2.5)
        
        text_file = open("txt/credits.txt", "r")
        text = text_file.read()
        text_file.close()
        
        credits.set_text(text)
        
        credits.set_text_position((self.width/20, self.height))
        self.app_parent.screen_open(credits)
    
    def quit_game(self):
        self.app_parent.screen_close()
                
    def draw(self):
        Screen.draw(self)
        self.menu.draw(self.display)
        self.title_text.draw(self.display)
        pygame.display.flip()
        

class InGameScreen(Screen):
    '''
    Facilitates the actual in-game session; 
    handles pausing/pause menu and returning to
    the TitleScreen.
    '''
    def __init__(self, width, height, app, display):
        Screen.__init__(self, width, height, app, display)
        
        self.set_bgm("BGM/aryx.s3m")
        self.set_bgm_volume(1.0)
        self.set_bgm_fadetime(1000)
        
        #self.set_bg_image("TitleBG.jpg")
        #self.set_bg_scaled(True)
        self.set_should_draw_bg(False)
        
        self.pause_menu = Menu("Paused")
        self.pause_menu.add_member(Menu("Quit to Title", InGameScreen.quit_title))
        self.pause_menu.set_position((self.display.get_width()/2, self.display.get_height()/3))
        
        self.set_paused(True)
        
    def start_game(self, difficulty, mode):
        self.game = Game(pygame.Rect(0, 0, self.display.get_width(), self.display.get_height()),difficulty, mode)
        
    def set_paused(self, paused):
        self.paused = paused
        
    def get_paused(self):
        return self.paused
    
    def toggle_paused(self):
        self.paused = not self.paused
        
    def activate(self):
        Screen.activate(self)
        
    def deactivate(self):
        Screen.deactivate(self)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_down(event.key)
        elif event.type == pygame.KEYUP:
            self.key_up(event.key)

    def key_down(self, key):
        if key == pygame.K_ESCAPE:
            self.toggle_paused()
            
        if self.paused:
            if key == pygame.K_RETURN:
                self.pause_menu.enter(self)
        else:
            self.game.key_down(key)
    
    def key_up(self, key):
        if self.paused == False:
            self.game.key_up(key)
        
    def update_game(self, frametime):
        self.game.update(frametime)
    
    
    def draw_game(self):
        self.game.draw(self.display)
    
    
    def update(self, frametime):
        if self.paused == False:
            self.update_game(frametime)
    
    def draw(self):
        Screen.draw(self)
        self.draw_game()
        if self.paused == True:
            self.pause_menu.draw(self.display)
            
        pygame.display.flip()
        
    def quit_title(self):
        self.app_parent.screen_close()
        
        
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
            
            Entity.__init__(self, 1, geometry, position, velocity, orientation, 0.0, 1.0)
            
            self.damage = damage
            
        def get_damage(self):
            return self.damage
        
    def __init__(self, hp, position, velocity, orientation):
        
        geometry = (Vector2D(-20, 20), Vector2D(10, 15),
                    Vector2D(30, 0),
                    Vector2D(10, -15), Vector2D(-20, -20))
        
        '''geometry = (Vector2D(-20, -20), Vector2D(10, -15),
                    Vector2D(30, 0),
                    Vector2D(10, 15), Vector2D(-20, 20))'''
        
        Entity.__init__(self, hp, geometry, position, velocity, orientation, 0.0, 1.0)
        
        self.has_shield = False
        self.shot_time = 0.5 
        self.shot_damage = 10
        self.shot_speed = 1000.0

        self.shot_timer = 0.0
        
        self.turn_speed = math.pi
        self.thrust = 10000.0
        
        self.accelerate(False)
        
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

    def update(self, dt):
        if self.accelerating == True:
            self.apply_oriented_force(self.thrust)
        Entity.update(self, dt)
        self.update_shot_timer(dt)
        
    #def draw(self, surface):
    #    self.draw_phys(surface)
    
class Asteroid(Entity):
    '''
    Avoid these
    '''
    def __init__(self, hp, position, velocity, orientation, ang_velocity):
        
        geometry = (Vector2D(-43, 0), Vector2D(-29, 21), Vector2D(0, 30), Vector2D(20, 28), Vector2D(40, 0), Vector2D(30, -28), Vector2D(0, -37), Vector2D(-29, -22))
        
        Entity.__init__(self, hp, geometry, position, velocity, orientation, ang_velocity, 1000.0)
       
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
        
        Entity.__init__(self, hp, tuple(geometry), position, velocity, orientation, ang_velocity, 1000000.0)
        
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
GAME_SETTINGS_EASY = {'distance': 1000, 'default_lives': 5, 'default_hp': 100, 'aster_freq': 1.0, 'hole_freq': 0.125, 'shield_freq': 0.25, 'weapon_freq': 0.25}
GAME_SETTINGS_MEDIUM = {'distance': 2000, 'default_lives': 3, 'default_hp': 100, 'aster_freq': 3.0, 'hole_freq': 0.25, 'shield_freq': 0.125, 'weapon_freq': 0.125}
GAME_SETTINGS_HARD = {'distance': 5000, 'default_lives': 2, 'default_hp': 100, 'aster_freq': 4.0, 'hole_freq': 0.30, 'shield_freq': 0.10, 'weapon_freq': 0.10 }
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
        self.player = Player(self.settings.default_hp, Vector2D(self.screen_rect.width/4, self.screen_rect.height/2), Vector2D(0,0), 0.0)
        self.add_entity(self.player)
    
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
        if isinstance(entity, Player.Shot):
                if self.screen_rect.colliderect(entity.get_bounding_rect()) == False:
                    self.entity_list.remove(entity)
                    return True
        else:
            return False
                    
    def wrap_player(self, entity):
        if isinstance(entity, Player):
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
        
    
    def update(self, frametime):
        self.star_field.update(frametime)
        self.dynamics.resolve_collisions(self.entity_list, frametime)
        for entity in self.entity_list:
            entity.update(frametime)
            if self.remove_offscreen_shot(entity) == False:
                self.wrap_player(entity)
                    
    
    def draw(self, surface):
        surface.fill((0,0,0))
        #self.star_field.draw(surface)
        for entity in self.entity_list:
            entity.draw(surface)
        