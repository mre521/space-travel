#
# screen.py - game screens functionality
# and other stuff
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

import pygame.mixer
import pygame.draw
import pygame.image
import pygame.font

import game

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
        pygame.mixer.music.fadeout(int(time))
        
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
        
        self.antialias = antialias
        self.underline = underline
        self.bold = bold
        self.italic = italic
        self.background = background
        self.color = color
        
        self.set_text(text)
            
        self.set_position((0,0))
        self.set_center_x(center_x)
        self.set_center_y(center_y)
        
    def set_text(self, text):
        self.text = text
        font = self.font
        font.set_underline(self.underline)
        font.set_bold(self.bold)
        font.set_italic(self.italic)
        
        # required for font.render to function properly when None is
        # given for background
        if self.background == None:
            self.surface = font.render(text, self.antialias, self.color).convert_alpha()
        else:
            self.surface = font.render(text, self.antialias, self.color, self.background).convert()
        
        
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
    '''
    Implements a text-based menu which
    can be navigated
    '''
    def __init__(self, title, enter_function=None, enter_and_call=False, title_font=MENU_TITLE_FONT, member_font=MENU_MEMBER_FONT):
        self.title = title
        self.enter_function = enter_function
        self.enter_and_call = enter_and_call
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
                if selected.enter_and_call == True:
                    selected.set_position(self.position)
                    return selected
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
        self.set_bgm_volume(1.0)
        self.set_bgm_fadetime(2000)
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
        
        self.set_font(TEXT_FONT)
        
        self.set_scroll(False)
        self.set_scroll_rate(0.0)
        
        self.rendered_lines = []
        
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
            
    def set_font(self, font):
        self.font = font
        
    def set_text_color(self, color):
        self.color = color
        
    def generate_lines(self):
        text_lines = self.text.split('\n')
        self.rendered_lines = []
        for line in text_lines:
            rendered = RenderedText(self.font, line, self.color)
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
    
    def draw_text(self, surface):
        for line in self.rendered_lines:
            line.draw(surface)
    
    def draw(self):
        self.display.fill((0,0,0))
        self.draw_text(self.display)
        pygame.display.flip()
        
    def go_back(self):
        self.app_parent.screen_close()
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.go_back()
        

TITLE_FONT = pygame.font.Font("fonts/Rase-GPL-Bold.otf", 50)
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
        
        self.title_text = RenderedText(TITLE_FONT, "SPACE TRAVEL", (0, 255, 0), True, True)
        self.title_text.set_position((self.display.get_width()/2, self.display.get_height()/6))
        
        self.menu = Menu("Main Menu")
        self.menu.set_position((self.display.get_width()/2, self.display.get_height()/3))
        
        start_menu = Menu("Start Game")
        
        
        easy = Menu("Easy Difficulty", TitleScreen.easy_difficulty)
        medium = Menu("Medium Difficulty", TitleScreen.medium_difficulty)
        hard = Menu("Hard Difficulty", TitleScreen.hard_difficulty)
        
        normal = Menu("Normal Game", TitleScreen.normal_mode, True)
        endurance = Menu("Endurance", TitleScreen.endurance_mode, True)
        
        normal.add_member(easy)
        normal.add_member(medium)
        normal.add_member(hard)
        
        endurance.add_member(easy)
        endurance.add_member(medium)
        endurance.add_member(hard)
        
        start_menu.add_member(normal)
        start_menu.add_member(endurance)
        
        self.menu.add_member(start_menu)
        self.menu.add_member(Menu("Story", TitleScreen.show_story))
        self.menu.add_member(Menu("Controls", TitleScreen.show_controls))
        self.menu.add_member(Menu("Hiscores", TitleScreen.show_hiscores))
        self.menu.add_member(Menu("Credits", TitleScreen.show_credits))
        self.menu.add_member(Menu("Exit", TitleScreen.quit_game))
        
        self.angle = 0
        self.prevrect = None
        
    def activate(self):
        Screen.activate(self)
        
        # get to top level menu
        while self.menu_exit():
            pass
        
    def deactivate(self):
        Screen.deactivate(self)
    
    def handle_event(self, event):
        '''
        Handle navigation of the main menu
        '''
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
        '''
        Select previous item
        '''
        self.menu.select_prev()
    
    def menu_next(self):
        '''
        Select next item
        '''
        self.menu.select_next()
        
    def menu_enter(self):
        '''
        Enter one level
        '''
        menu = self.menu.enter(self)
        if type(menu) == type(self.menu):
            self.menu = menu

    def menu_exit(self):
        '''
        Go up one level
        '''
        menu = self.menu.exit()
        if type(menu) == type(self.menu):
            self.menu = menu
            return True
        else:
            return False
        
    def easy_difficulty(self):
        self.game_diff = game.GAME_DIFF_EASY
        self.start_game()
        
    def medium_difficulty(self):
        self.game_diff = game.GAME_DIFF_MEDIUM
        self.start_game()
        
    def hard_difficulty(self):
        self.game_diff = game.GAME_DIFF_HARD
        self.start_game()
        
    def normal_mode(self):
        self.game_mode = game.GAME_MODE_NORMAL
        
    def endurance_mode(self):
        self.game_mode = game.GAME_MODE_ENDURANCE
        
    def start_game(self):
        '''
        Start game with selected mode and
        difficulty
        '''
        gamescreen = InGameScreen(self.width, self.height, self.app_parent, self.display)
        gamescreen.start_game(self.game_diff, self.game_mode)
        self.app_parent.screen_open(gamescreen)
            
    def show_story(self):
        '''
        Show the game story
        '''
        story = TextScreen(self.width, self.height, self.app_parent, self.display)
        story.set_text_color((255,255,255))
        
        text_file = open("txt/story.txt", "r")
        text = text_file.read()
        text_file.close()
        
        story.set_text(text)
        
        story.set_text_position((self.width/20, self.height/20))
        self.app_parent.screen_open(story)
        
    def show_controls(self):
        '''
        Show the controls information
        '''
        controls_screen = TextScreen(self.width, self.height, self.app_parent, self.display)
        controls_screen.set_text_color((255,255,255))
        
        text_file = open("txt/controls.txt", "r")
        text = text_file.read()
        text_file.close()
        
        controls_screen.set_text(text)
        
        controls_screen.set_text_position((self.width/20, self.height/20))
        self.app_parent.screen_open(controls_screen)
        
    def show_hiscores(self):
        '''
        Open the hiscores
        '''
        hiscores_screen = HiscoresScreen(self.width, self.height, self.app_parent, self.display)
        self.app_parent.screen_open(hiscores_screen)
            
    def show_credits(self):
        '''
        Roll the credits
        '''
        credits_screen = TextScreen(self.width, self.height, self.app_parent, self.display)
        credits_screen.set_text_color((255,255,255))
        credits_screen.set_scroll(True)
        credits_screen.set_scroll_rate(1.5)
        
        text_file = open("txt/credits.txt", "r")
        text = text_file.read()
        text_file.close()
        
        credits_screen.set_text(text)
        
        credits_screen.set_bgm("BGM/hymn to aurora.mod")
        credits_screen.set_text_position((self.width/20, self.height))
        self.app_parent.screen_open(credits_screen)
    
    def quit_game(self):
        '''
        Get out of this program
        '''
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
        

        self.set_should_draw_bg(False)
        
        self.pause_menu = Menu("Paused")
        self.pause_menu.add_member(Menu("Quit to Title", InGameScreen.quit_title))
        self.pause_menu.set_position((self.display.get_width()/2, self.display.get_height()/3))
        
        self.set_paused(False)
        
    def start_game(self, difficulty, mode):
        self.game = game.Game(pygame.Rect(0, 0, self.display.get_width(), self.display.get_height()),difficulty, mode)
        
    def set_paused(self, paused):
        self.paused = paused
        
    def get_paused(self):
        return self.paused
    
    def toggle_paused(self):
        self.paused = not self.paused
        
    def handle_event(self, event):
        '''
        Detects key presses and when
        the Game wants to show Hiscores.
        '''
        if event.type == pygame.KEYDOWN:
            self.key_down(event.key)
        elif event.type == pygame.KEYUP:
            self.key_up(event.key)
        elif event.type == game.GAME_SHOW_HISCORES:
            self.show_hiscores()
        elif event.type == game.GAME_SHOW_TITLE:
            self.quit_title()

    def key_down(self, key):
        '''
        Notify game of key down,
        or open pause menu
        '''
        if key == pygame.K_ESCAPE:
            self.toggle_paused()
            
        if self.paused:
            if key == pygame.K_RETURN:
                self.pause_menu.enter(self)
        else:
            self.game.key_down(key)
    
    def key_up(self, key):
        '''
        Notify game of key up
        '''
        if self.paused == False:
            self.game.key_up(key)
        
    def update_game(self, frametime):
        self.game.update(frametime)
    
    
    def draw_game(self):
        self.game.draw(self.display)
    
    
    def update(self, frametime):
        '''
        Update game as long as it's not paused
        '''
        if self.paused == False:
            self.update_game(frametime)
    
    def draw(self):
        '''
        Draw game and pause menu
        if its open.
        '''
        Screen.draw(self)
        self.draw_game()
        if self.paused == True:
            self.pause_menu.draw(self.display)
            
        pygame.display.flip()
        
    def show_hiscores(self):
        '''
        Close this screen but open Hiscores at the same time,
        adding a new entry for the game just played.
        '''
        hiscores_screen = HiscoresScreen(self.width, self.height, self.app_parent, self.display)
        if self.game.get_game_won() == True:
            hiscores_screen.add_game_entry(self.game)
        self.app_parent.screen_close(hiscores_screen)
        
    def quit_title(self):
        '''
        Go to title screen
        '''
        self.app_parent.screen_close()

HISCORES_FONT = pygame.font.Font("fonts/NEW ACADEMY.ttf", 18)
HISCORES_TITLE_FONT = pygame.font.Font("fonts/Rase-GPL-Bold.otf", 50)
HISCORES_TITLE_COLOR = (127,255,255)
HISCORES_TEXT_COLOR = (255,255,0)
HISCORES_SCROLL_DELAY = 5.0 # 5 seconds delay
HISCORES_SCROLL_RATE = 0.5 # 0.5 lines per second
class HiscoresScreen(TextScreen):
    '''
    Allows players to brag about their scores
    '''
    class ScoreEntry(object):
        '''
        One player's success.
        '''
        def __init__(self, name, distance, points):
            self.name = name
            self.distance = distance
            self.points = points
            
        def get_name(self):
            return self.name
        
        def get_distance(self):
            return "%.2f"%(self.distance)
        
        def get_points(self):
            return str(self.points)
        
        @staticmethod
        def from_file(file_obj):
            '''
            Create a ScoreEntry from given file
            '''
            name = file_obj.readline().replace('\n','')
            distance = float(file_obj.readline().replace('\n',''))
            points = int(file_obj.readline().replace('\n',''))
            
            return HiscoresScreen.ScoreEntry(name, distance, points)
        
        def to_file(self, file_obj):
            '''
            Save this ScoreEntry to given file
            '''
            file_obj.write(self.get_name() + '\n')
            file_obj.write(self.get_distance() + '\n')
            file_obj.write(self.get_points() + '\n')
            
    def __init__(self, width, height, app, display):
        TextScreen.__init__(self, width, height, app, display)
        
        self.score_entries = []
        self.title = "Hiscores"
        self.title_text = RenderedText(HISCORES_TITLE_FONT, self.title, HISCORES_TITLE_COLOR, True)
        self.title_text.set_position((self.width/2, self.height/20))
        
        try:
            self.load_scores()
        except:
            print "No hiscores yet."
            
        self.set_font(HISCORES_FONT)
            
        self.create_scores_text()
            
        self.adding_entry = False
        self.scroll_pause_timer = HISCORES_SCROLL_DELAY # pause for 4 seconds before starting to scroll
        self.set_scroll_rate(HISCORES_SCROLL_RATE) # 1 line per second
        self.set_scroll(False)
            
        self.set_bgm("BGM/stardstm.mod")
        self.set_bg_image("BG/Hiscores.jpg")
        self.set_bg_scaled(True)
        self.set_should_draw_bg(True)
        
    def load_scores(self):
        '''
        Load the hiscores from file
        '''
        
        scores = open("hiscores.dat", "r")
        
        self.score_entries = []
        
        try:
            while True:
                self.score_entries.append(HiscoresScreen.ScoreEntry.from_file(scores))
        except:
            pass 
        
        scores.close()
        
    def save_scores(self):
        '''
        Records hiscores to file.
        '''
        scores = open("hiscores.dat", "w")
        
        for entry in self.score_entries:
            entry.to_file(scores)
            
        scores.close()
    
    def add_game_entry(self, game):
        '''
        Add an entry into the hiscores from
        the game just played
        '''
        self.adding_entry = True
        self.game = game
        
        enter_position = (self.width/2, self.height/2)
        
        self.enter_name_text = RenderedText(HISCORES_FONT, "Please enter your name: ", HISCORES_TEXT_COLOR, True, True)
        self.enter_name_text.set_position(enter_position)
        
        self.name_text = RenderedText(HISCORES_FONT, "", HISCORES_TEXT_COLOR, True, True)
        self.name_text.set_position((enter_position[0], enter_position[1]+self.enter_name_text.get_height()))
        self.name_string = ""
        
    def handle_event(self, event):
        '''
        Handle the keyboard
        '''
        if self.adding_entry == True:
            if event.type == pygame.KEYDOWN: 
                mods = pygame.key.get_mods()
                key = event.key
                
                if key >= 32 and key <= 126 or key == pygame.K_RETURN or key == pygame.K_BACKSPACE:
                    # only detect printable characters
                    if mods & pygame.KMOD_SHIFT:
                        if key >= 97 and key <= 122:
                            # make shift for letters work
                            key -= 32
                        if key >= 91 and key <= 94:
                            # and for some symbols as well
                            key += 32
                            
                    # actually type the processed key
                    self.type_name(key)
        else:
            TextScreen.handle_event(self, event)
            
    def type_name(self, key):
        '''
        handle keyboard when entering
        a new hiscore
        '''
        if key == pygame.K_RETURN:
            entry = HiscoresScreen.ScoreEntry(self.name_string, self.game.get_final_distance(), self.game.get_final_points())
            self.score_entries.append(entry)
            self.save_scores()
            self.create_scores_text()
            self.adding_entry = False
        else:
            if key == pygame.K_BACKSPACE:
                try:
                    self.name_string = self.name_string[0:-1]
                except:
                    pass
            else:
                self.name_string = self.name_string + chr(key)
            self.name_text.set_text(self.name_string)
            self.name_text.set_center_x(True)
            
    def create_scores_text(self):
        '''
        Creates the rendered text lines
        for the loaded hiscores.
        '''
        rank = 1
        text = ""
        if len(self.score_entries) > 0:
            for entry in self.score_entries:
                entry_text = "#" + str(rank) + ". " + entry.get_name() + " traveled a distance of " + entry.get_distance() + " and scored " + entry.get_points() + " points.\n"
                text += entry_text
                rank += 1
        else:
            text = "Nothing here..."
        
        self.set_text_color(HISCORES_TEXT_COLOR)
        self.set_text(text)
        self.set_text_position((self.width/40, self.height/6))
        
        
    def add_score_update(self, dt):
        pass
    
    def add_score_draw(self, surface):
        '''
        Draw the text when entering a new
        hiscore.
        '''
        self.enter_name_text.draw(surface)
        self.name_text.draw(surface)
    
    def scores_update(self, dt):
        '''
        Update the screen when not entering a
        new hiscore.
        '''
        TextScreen.update(self, dt)
        # update scroll pause timer and
        # turn on scrolling when it expires
        if self.scroll_pause_timer > 0.0:
            self.scroll_pause_timer -= dt
            if self.scroll_pause_timer <= 0:
                self.scroll_pause_timer = 0.0
                self.set_scroll(True)
    
    def scores_draw(self, surface):
        '''for entry in self.score_entries:
                entry_text = "#" + str(rank) + ". " + entry.get_name() + " traveled a distance of " + entry.get_distance() + " and scored " + entry.get_points() + " points.\n"
                text += entry_text
                rank += 1
        Show the hiscores on the screen
        '''
        TextScreen.draw_text(self, surface)
    
    def update(self, dt):
        TextScreen.update(self, dt)
        if self.adding_entry:
            self.add_score_update(dt)
        else:
            self.scores_update(dt)
            
    def draw(self):
        self.bg.draw(self.display)
        
        if self.adding_entry:
            self.add_score_draw(self.display)
        else:
            self.scores_draw(self.display)
            
        # draw title on top of everything
        self.title_text.draw(self.display)
            
        pygame.display.flip()