#
# app.py - game entry point and top level framework
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

# imports
import pygame.display
import pygame.time
import pygame.event

import screen
        
class AppState(object):
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 600
    FRAMERATE = 60
    WINDOWED = True

    # state vars
    display = None
    clock = None
    active = False
    
    # list of game screens, updated dynamically
    screens = [None]
    
    # previous frame's time taken in seconds   
    frametime = 1.0/FRAMERATE
    

    def __init__(self):
        pass

    # create pygame window with appropriate properties
    def setup_display(self):
        flags = pygame.DOUBLEBUF
        if not self.WINDOWED:
            flags |= pygame.FULLSCREEN
        self.display = pygame.display.set_mode(
            [self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT],
            flags)

        self.clock = pygame.time.Clock()

    # store frametime in correct units
    def set_frametime(self,milliseconds):
        # frametime has units of seconds
        # 1000ms in 1 second
        # seconds = ms/1000 seconds
        self.frametime = milliseconds/1000.0
        
    def get_open_screen(self):
        return self.screens[-1]
    
    def screen_close(self):
        '''
        Called by the currently open Screen to close itself.
        '''
        screen = self.screens.pop()
        screen.deactivate()
        
        screen = self.get_open_screen()
        if screen != None:
            screen.activate()
        
    def screen_open(self, new):
        '''
        Called by the currently open Screen to open a new
        Screen.
        '''
        screen = self.get_open_screen()
        screen.deactivate()
        
        new.activate()
        self.screens.append(new)

    def handle_events(self, events, screen):
        screen.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.active = False; # close button clicked
        

    def update_state(self, screen, frametime):
        events = pygame.event.get()
        self.handle_events(events, screen)
        screen.update(frametime)

    # show the result of everything
    def draw_graphics(self, screen):
        screen.draw()

    
    # all game code runs from here
    # updates state and graphics
    def loop(self):
        self.active = True
        
        screen = self.get_open_screen()

        while self.active:
            self.update_state(screen, self.frametime)
            self.draw_graphics(screen)
            
            millis =  self.clock.tick(self.FRAMERATE) # limit app speed
            self.set_frametime(millis) 
            
            screen = self.get_open_screen()
            if screen == None:
                self.active = False

    # starts everything
    def run(self):
        pygame.init()
        self.setup_display()
        
        titleScreen = screen.TitleScreen(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, self, self.display)
        titleScreen.activate()
        self.screens.append(titleScreen)
        
        self.loop() # does not return until game is finished
        self.stop()

    def stop(self):
        pygame.quit()


def main():
    print '''PygameGame Copyright (C) 2014  Eric Eveleigh
This program comes with ABSOLUTELY NO WARRANTY; for details see LICENSE
This is free software, and you are welcome to redistribute it
under certain conditions; for details see LICENSE.'''
    
    app = AppState()
    app.run()

if __name__=="__main__":
    main()
